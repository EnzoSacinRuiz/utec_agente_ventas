"""Herramienta para verificar blacklist"""
from langchain.tools import tool
from src.config.settings import BLACKLIST_NUMBERS

@tool
def verificar_blacklist(identificador: str) -> str:
    """
    Verifica si un número de teléfono o identificador está en la lista negra.
    
    Args:
        identificador: Número de teléfono o ID del usuario
        
    Returns:
        "BLOQUEADO" si está en blacklist, "OK" si no lo está
    """
    identificador_limpio = identificador.strip().replace(" ", "").replace("-", "")
    
    if identificador_limpio in BLACKLIST_NUMBERS:
        return "BLOQUEADO - Usuario en lista negra"
    
    return "OK - Usuario válido"