"""Lead Qualifier Agent - Filtro inicial del sistema"""
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.schema import HumanMessage, AIMessage

from src.config.settings import (
    MODEL_NAME, 
    TEMPERATURE, 
    MEMORY_WINDOW_SIZE,
    OPENAI_API_KEY,
    ANTHROPIC_API_KEY
)
from src.prompts.lead_qualifier_prompt import LEAD_QUALIFIER_PROMPT
from src.tools.blacklist import verificar_blacklist


class LeadQualifier:
    """
    Agente Lead Qualifier - Primera línea de filtrado
    
    Responsabilidades:
    - Clasificar intención del mensaje
    - Detectar spam y mensajes off-topic
    - Mantener contador de mensajes irrelevantes
    - Decidir si escalar a humano
    """
    
    def __init__(self):
        # Inicializar LLM según configuración
        if "claude" in MODEL_NAME.lower():
            self.llm = ChatAnthropic(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                anthropic_api_key=ANTHROPIC_API_KEY
            )
        else:
            self.llm = ChatOpenAI(
                model=MODEL_NAME,
                temperature=TEMPERATURE,
                openai_api_key=OPENAI_API_KEY
            )
        
        # Memory: últimas 3 interacciones
        self.memory = ConversationBufferWindowMemory(
            k=MEMORY_WINDOW_SIZE,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Contador de mensajes off-topic
        self.contador_off_topic = 0
        
        # Tools disponibles
        self.tools = [verificar_blacklist]
        
        # Setup del agente
        self._setup_agent()
    
    def _setup_agent(self):
        """Configura el agente con prompt y tools"""
        # Por ahora usamos modo simple sin tools para empezar
        # Luego agregaremos create_tool_calling_agent
        self.prompt_template = PromptTemplate(
            template=LEAD_QUALIFIER_PROMPT,
            input_variables=["mensaje", "historial", "contador_off_topic"]
        )
    
    def _get_historial(self) -> str:
        """Obtiene el historial de conversación formateado"""
        messages = self.memory.chat_memory.messages
        if not messages:
            return "No hay historial previo."
        
        historial = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                historial.append(f"Cliente: {msg.content}")
            elif isinstance(msg, AIMessage):
                historial.append(f"Sistema: {msg.content}")
        
        return "\n".join(historial)
    
    def procesar_mensaje(self, mensaje: str, identificador: str = None) -> Dict[str, Any]:
        """
        Procesa un mensaje del cliente
        
        Args:
            mensaje: Texto del mensaje del cliente
            identificador: Número de teléfono o ID del cliente (opcional)
            
        Returns:
            Dict con la clasificación y acción a tomar
        """
        # 1. Verificar blacklist si hay identificador
        if identificador:
            resultado_blacklist = verificar_blacklist.invoke({"identificador": identificador})
            if "BLOQUEADO" in resultado_blacklist:
                return {
                    "intencion": "spam",
                    "accion": "bloquear",
                    "razonamiento": "Usuario en lista negra",
                    "bloqueado": True
                }
        
        # 2. Preparar el prompt
        historial = self._get_historial()
        prompt_completo = self.prompt_template.format(
            mensaje=mensaje,
            historial=historial,
            contador_off_topic=self.contador_off_topic
        )
        
        # 3. Llamar al LLM
        respuesta = self.llm.invoke(prompt_completo)
        
        # 4. Parsear respuesta JSON
        try:
            # Limpiar la respuesta por si tiene markdown
            contenido = respuesta.content.strip()
            if contenido.startswith("```json"):
                contenido = contenido[7:]
            if contenido.startswith("```"):
                contenido = contenido[3:]
            if contenido.endswith("```"):
                contenido = contenido[:-3]
            
            resultado = json.loads(contenido.strip())
        except json.JSONDecodeError as e:
            print(f"❌ Error parseando JSON: {e}")
            print(f"Respuesta recibida: {respuesta.content}")
            resultado = {
                "intencion": "error",
                "accion": "error",
                "razonamiento": "Error en el formato de respuesta"
            }
        
        # 5. Actualizar contador off-topic
        if resultado.get("es_off_topic", False):
            self.contador_off_topic += 1
            print(f"⚠️  Contador off-topic: {self.contador_off_topic}/3")
            
            if self.contador_off_topic >= 3:
                resultado["accion"] = "escalar_humano"
                resultado["razonamiento"] += " | 3 mensajes off-topic detectados"
        else:
            # Reset si el mensaje es relevante
            if resultado.get("intencion") not in ["off-topic", "spam"]:
                self.contador_off_topic = 0
        
        # 6. Guardar en memoria
        self.memory.chat_memory.add_user_message(mensaje)
        self.memory.chat_memory.add_ai_message(json.dumps(resultado, ensure_ascii=False))
        
        return resultado
    
    def reset(self):
        """Resetea el estado del agente (nueva conversación)"""
        self.memory.clear()
        self.contador_off_topic = 0
        print("🔄 Lead Qualifier reseteado")