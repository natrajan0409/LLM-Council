import google.generativeai as genai
import sys

# Get API key from command line
if len(sys.argv) < 2:
    print("Usage: python debug_gemini.py YOUR_API_KEY")
    sys.exit(1)

api_key = sys.argv[1]

try:
    genai.configure(api_key=api_key)
    
    print("Fetching available Gemini models...")
    models = genai.list_models()
    
    print("\nAll models:")
    for m in models:
        print(f"  - {m.name}")
        print(f"    Supported methods: {m.supported_generation_methods}")
    
    print("\n\nModels that support generateContent:")
    content_models = [
        m.name for m in models 
        if 'generateContent' in m.supported_generation_methods
    ]
    
    for model in content_models:
        print(f"  ✓ {model}")
    
    if not content_models:
        print("  ⚠️  No models found that support generateContent!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
