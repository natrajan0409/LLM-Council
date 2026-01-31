import ollama
import json

try:
    models = ollama.list()
    print("Raw Ollama List Output:")
    print(json.dumps(models, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")
