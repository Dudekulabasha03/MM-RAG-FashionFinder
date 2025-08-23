"""
Configuration settings for the Style Finder application.
"""

# Ollama LLM configuration
OLLAMA_MODEL_NAME = "llama3.2:3b"
OLLAMA_BASE_URL = "http://localhost:11434"

# Image processing settings
IMAGE_SIZE = (224, 224)
NORMALIZATION_MEAN = [0.485, 0.456, 0.406]
NORMALIZATION_STD = [0.229, 0.224, 0.225]

# Default similarity threshold
SIMILARITY_THRESHOLD = 0.8

# Number of alternatives to return from search
DEFAULT_ALTERNATIVES_COUNT = 5
