"""Configuración centralizada del proyecto"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model settings
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = 0.3  # Más bajo = más determinístico

# Memory settings
MEMORY_WINDOW_SIZE = 3  # Lead Qualifier recuerda últimas 3 interacciones

# Blacklist
BLACKLIST_NUMBERS = ["123456789", "999999999", "spam_user"]