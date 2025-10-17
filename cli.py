"""CLI para probar el Lead Qualifier desde la terminal"""
import sys
from colorama import init, Fore, Style
from src.agents.lead_qualifier import LeadQualifier

# Inicializar colorama para colores en terminal
init(autoreset=True)


def imprimir_banner():
    """Imprime el banner inicial"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}🤖  LEAD QUALIFIER - Sistema de Ventas Médicas")
    print(f"{Fore.CYAN}{'='*60}\n")
    print(f"{Fore.YELLOW}Comandos disponibles:")
    print(f"  {Fore.GREEN}/reset{Fore.WHITE}  - Reiniciar conversación")
    print(f"  {Fore.GREEN}/salir{Fore.WHITE}  - Salir del sistema")
    print(f"  {Fore.GREEN}/estado{Fore.WHITE} - Ver estado del agente")
    print(f"\n{Fore.CYAN}Escribe tu mensaje como si fueras un cliente:\n")


def imprimir_resultado(resultado: dict):
    """Imprime el resultado de forma visual"""
    # Color según la acción
    if resultado.get("accion") == "escalar_humano":
        color_accion = Fore.RED
        emoji = "🚨"
    elif resultado.get("accion") == "bloquear":
        color_accion = Fore.MAGENTA
        emoji = "🚫"
    else:
        color_accion = Fore.GREEN
        emoji = "✅"
    
    print(f"\n{Fore.CYAN}{'─'*60}")
    print(f"{emoji} {Fore.WHITE}Intención: {Fore.YELLOW}{resultado.get('intencion', 'N/A')}")
    print(f"{emoji} {Fore.WHITE}Acción: {color_accion}{resultado.get('accion', 'N/A')}")
    print(f"{emoji} {Fore.WHITE}Prioridad: {Fore.BLUE}{resultado.get('prioridad', 'N/A')}")
    
    if resultado.get('datos'):
        datos = resultado['datos']
        if datos.get('nombre'):
            print(f"👤 {Fore.WHITE}Nombre detectado: {Fore.GREEN}{datos['nombre']}")
        print(f"😊 {Fore.WHITE}Tono: {Fore.MAGENTA}{datos.get('tono', 'N/A')}")
    
    if resultado.get('razonamiento'):
        print(f"\n💭 {Fore.WHITE}Razonamiento:")
        print(f"   {Fore.LIGHTBLACK_EX}{resultado['razonamiento']}")
    
    if resultado.get('riesgo'):
        print(f"\n⚠️  {Fore.RED}Riesgo: {resultado['riesgo']}")
    
    print(f"{Fore.CYAN}{'─'*60}\n")


def main():
    """Función principal del CLI"""
    imprimir_banner()
    
    # Inicializar agente
    print(f"{Fore.YELLOW}⏳ Inicializando Lead Qualifier...")
    try:
        agente = LeadQualifier()
        print(f"{Fore.GREEN}✅ Lead Qualifier listo!\n")
    except Exception as e:
        print(f"{Fore.RED}❌ Error inicializando: {e}")
        print(f"{Fore.YELLOW}💡 Asegúrate de tener tu API key en el archivo .env")
        sys.exit(1)
    
    # Loop principal
    while True:
        try:
            # Leer input del usuario
            mensaje = input(f"{Fore.GREEN}Cliente > {Style.RESET_ALL}").strip()
            
            if not mensaje:
                continue
            
            # Comandos especiales
            if mensaje.lower() == "/salir":
                print(f"\n{Fore.CYAN}👋 ¡Hasta luego!")
                break
            
            elif mensaje.lower() == "/reset":
                agente.reset()
                continue
            
            elif mensaje.lower() == "/estado":
                print(f"\n{Fore.CYAN}📊 Estado del agente:")
                print(f"   Contador off-topic: {agente.contador_off_topic}/3")
                print(f"   Mensajes en memoria: {len(agente.memory.chat_memory.messages)}")
                print()
                continue
            
            # Procesar mensaje normal
            print(f"{Fore.YELLOW}⏳ Analizando...")
            resultado = agente.procesar_mensaje(mensaje)
            imprimir_resultado(resultado)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.CYAN}👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}\n")


if __name__ == "__main__":
    main()