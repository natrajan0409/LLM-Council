import ollama
import os
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

# External SDKs
try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Provider Interface ---

class LLMProvider(ABC):
    @abstractmethod
    def list_models(self) -> List[str]:
        pass

    @abstractmethod
    def generate_response(self, model: str, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None) -> str:
        pass

# --- Implementations ---

class OllamaProvider(LLMProvider):
    def list_models(self) -> List[str]:
        try:
            models_info = ollama.list()
            if hasattr(models_info, 'models'):
                return [m.model for m in models_info.models]
            if isinstance(models_info, dict) and 'models' in models_info:
                return [m.get('model', m.get('name')) for m in models_info['models']]
            return []
        except Exception as e:
            return [f"Error: {e}"]

    def generate_response(self, model: str, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None) -> str:
        messages = [{'role': 'system', 'content': system_prompt}]
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': prompt})
        
        try:
            response = ollama.chat(model=model, messages=messages)
            return response['message']['content']
        except Exception as e:
            return f"Ollama Error: {e}"

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)

    def list_models(self) -> List[str]:
        # Hardcoded popular models to avoid fetching 100s of niche ones, or fetch real ones
        try:
            # Simple list for POC
            return ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        except:
            return ["gpt-3.5-turbo"]

    def generate_response(self, model: str, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None) -> str:
        messages = [{'role': 'system', 'content': system_prompt}]
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': prompt})

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {e}"

class AnthropicProvider(LLMProvider):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def list_models(self) -> List[str]:
        return ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]

    def generate_response(self, model: str, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None) -> str:
        # Anthropic doesn't use 'system' in messages list usually, it's a top level param
        # Also history must alternate user/assistant.
        
        # Simple history conversion
        clean_history = []
        if history:
            for msg in history:
                if msg['role'] in ['user', 'assistant']:
                    clean_history.append(msg)
        
        clean_history.append({'role': 'user', 'content': prompt})

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_prompt,
                messages=clean_history
            )
            return message.content[0].text
        except Exception as e:
            return f"Anthropic Error: {e}"

class GoogleProvider(LLMProvider):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)

    def list_models(self) -> List[str]:
        try:
            # Dynamically fetch models that support content generation
            # Returns internal names like 'models/gemini-1.5-flash'
            return [
                m.name for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            ]
        except Exception as e:
            return [f"Error fetching Gemini models: {e}"]

    def generate_response(self, model: str, prompt: str, system_prompt: str, history: List[Dict[str, str]] = None) -> str:
        try:
            # Gemini has different history format (history is passed to start_chat)
            # content parts etc. For simple POC, we can just use generate_content with a big prompt
            # or try to use chat session.
            
            gemini_model = genai.GenerativeModel(model, system_instruction=system_prompt)
            
            chat_history = []
            if history:
                for h in history:
                    role = "user" if h["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [h["content"]]})
            
            chat = gemini_model.start_chat(history=chat_history)
            response = chat.send_message(prompt)
            return response.text
        except Exception as e:
            return f"Gemini Error: {e}"


class OpenRouterProvider(OpenAIProvider):
    def __init__(self, api_key: str):
        # OpenRouter/OpenCode uses the same OpenAI Client, just different Base URL
        self.client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )

    def list_models(self) -> List[str]:
        # OpenRouter has 100s of models. We unfortunately can't list them easily via standard OpenAI 'list' 
        # because the return format might be huge or require requests to a different endpoint.
        # But let's try standard list() first, usually standard OpenAI client supports it.
        try:
            models = self.client.models.list()
            # Sort by ID for easier finding
            return sorted([m.id for m in models.data])
        except Exception as e:
            # Fallback to some popular ones if list fails
            return ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-pro-1.5"]

# --- Council Core ---

class CouncilMember:
    def __init__(self, provider: LLMProvider, model_name: str, role: str = "Council Member"):
        self.provider = provider
        self.model_name = model_name
        self.role = role

    def get_opinion(self, prompt: str, chat_history: List[Dict[str, str]] = None) -> str:
        system_prompt = f"You are a member of an LLM Council. Your role is {self.role}. Provide a detailed and unique perspective on the user's query."
        return self.provider.generate_response(self.model_name, prompt, system_prompt, chat_history)

class Chairman:
    def __init__(self, provider: LLMProvider, model_name: str):
        self.provider = provider
        self.model_name = model_name

    def synthesize(self, user_query: str, council_opinions: List[Dict[str, str]], chat_history: List[Dict[str, str]] = None) -> str:
        opinions_text = ""
        for opinion in council_opinions:
            opinions_text += f"\n--- Opinion from {opinion['role']} ({opinion['model']}) ---\n{opinion['content']}\n"

        system_prompt = (
            "You are the Chairman of an LLM Council. "
            "Your goal is to synthesize the best parts of the council members' opinions into a single, high-quality, refined response for the user. "
            "Critically evaluate the input opinions, resolve contradictions, and provide the most accurate and helpful answer. "
            "Do not strictly mention 'Member 1 said this', but rather synthesize the information seamlessly unless attribution is necessary for clarity."
        )
        
        final_prompt = f"User Query: {user_query}\n\nCouncil Opinions:\n{opinions_text}\n\nChairman, please provide your synthesized response:"
        
        return self.provider.generate_response(self.model_name, final_prompt, system_prompt, chat_history)

def get_provider_implementation(provider_name: str, api_key: str = None) -> Optional[LLMProvider]:
    if provider_name == "Ollama":
        return OllamaProvider()
    elif provider_name == "OpenCode" and api_key:
        return OpenAIProvider(api_key)
    elif provider_name == "Claude Code" and api_key:
        return AnthropicProvider(api_key)
    elif provider_name == "Antigravity" and api_key:
        return GoogleProvider(api_key)
    elif provider_name == "OpenRouter" and api_key:
        return OpenRouterProvider(api_key)
    return None
