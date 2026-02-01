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
    def __init__(self, optimize_speed: bool = True):
        """
        Initialize Ollama provider with optional speed optimizations.
        
        Args:
            optimize_speed: If True, use settings optimized for faster responses
        """
        self.optimize_speed = optimize_speed
    
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
        
        # Performance optimization options for local models
        options = {}
        if self.optimize_speed:
            options = {
                'num_ctx': 2048,        # Reduced context window for faster processing
                'num_predict': 512,     # Limit response length for speed
                'temperature': 0.7,     # Slightly lower for more focused responses
                'top_p': 0.9,          # Nucleus sampling
                'top_k': 40,           # Limit token selection
            }
        
        try:
            response = ollama.chat(
                model=model, 
                messages=messages,
                options=options
            )
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
    def __init__(self, api_key: str = None, credentials=None):
        if api_key:
            genai.configure(api_key=api_key)
        elif credentials:
            genai.configure(credentials=credentials)
        else:
            raise ValueError("Either api_key or credentials must be provided")

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

# --- Debate-Style Council ---

class Proponent:
    """Generates the initial comprehensive response (Step 1)"""
    def __init__(self, provider: LLMProvider, model_name: str):
        self.provider = provider
        self.model_name = model_name

    def generate_draft(self, prompt: str, chat_history: List[Dict[str, str]] = None) -> str:
        system_prompt = (
            "You are a highly capable AI assistant. "
            "Provide a comprehensive, accurate, and well-reasoned response to the user's query. "
            "Be thorough and consider multiple perspectives."
        )
        return self.provider.generate_response(self.model_name, prompt, system_prompt, chat_history)


class Opponent:
    """Acts as Senior Logic Auditor to find flaws (Step 2)"""
    def __init__(self, provider: LLMProvider, model_name: str):
        self.provider = provider
        self.model_name = model_name

    def critique(self, user_query: str, proponent_output: str, chat_history: List[Dict[str, str]] = None) -> str:
        system_prompt = (
            "You are a Senior Logic Auditor. Your job is to find logic gaps, factual errors, "
            "missing edge cases, or weak reasoning in the provided response. "
            "You are FORBIDDEN from being nice. Be critical and thorough. "
            "If the response is accurate and complete with no significant flaws, you MUST say 'No critical flaws found.' "
            "Otherwise, provide specific, actionable critique pointing out exactly what is wrong or missing."
        )
        
        critique_prompt = f"""Original User Query: {user_query}

Response to Audit:
{proponent_output}

Please audit this response for accuracy, completeness, and logical soundness."""
        
        return self.provider.generate_response(self.model_name, critique_prompt, system_prompt, chat_history)


class DebateChairman:
    """Synthesizes final response incorporating valid critiques (Step 4)"""
    def __init__(self, provider: LLMProvider, model_name: str):
        self.provider = provider
        self.model_name = model_name

    def synthesize(self, user_query: str, proponent_output: str, critique_output: str, chat_history: List[Dict[str, str]] = None) -> str:
        system_prompt = (
            "You are the Chairman of an LLM Council. "
            "Review the Draft response and the Feedback from the Logic Auditor. "
            "Incorporate valid corrections and improvements while ignoring irrelevant nitpicks. "
            "Output the final, battle-hardened answer that addresses the user's query accurately and completely."
        )
        
        synthesis_prompt = f"""User Query: {user_query}

Draft Response:
{proponent_output}

Logic Auditor Feedback:
{critique_output}

Chairman, please provide your final synthesized response:"""
        
        return self.provider.generate_response(self.model_name, synthesis_prompt, system_prompt, chat_history)


class DebateCouncil:
    """Orchestrates the Proponent → Opponent → Chairman debate flow with short-circuit logic"""
    def __init__(self, proponent: Proponent, opponent: Opponent, chairman: DebateChairman):
        self.proponent = proponent
        self.opponent = opponent
        self.chairman = chairman

    def deliberate(self, user_query: str, chat_history: List[Dict[str, str]] = None) -> Dict[str, any]:
        """
        Execute the debate flow and return results with transparency trace.
        
        Returns:
            Dict with keys:
            - 'final_response': The final answer to return to user
            - 'trace': List of steps taken (for transparency)
            - 'short_circuit': Boolean indicating if short-circuit was triggered
        """
        trace = []
        
        # Step 1: Proponent generates initial draft
        proponent_output = self.proponent.generate_draft(user_query, chat_history)
        trace.append({
            'step': 'Proponent',
            'model': self.proponent.model_name,
            'output': proponent_output
        })
        
        # Step 2: Opponent critiques the draft
        critique_output = self.opponent.critique(user_query, proponent_output, chat_history)
        trace.append({
            'step': 'Opponent (Logic Auditor)',
            'model': self.opponent.model_name,
            'output': critique_output
        })
        
        # Step 3: Short-circuit check
        short_circuit_phrases = [
            "no critical flaws found",
            "the response is accurate",
            "no significant issues",
            "no major flaws",
            "response is correct"
        ]
        
        critique_lower = critique_output.lower()
        should_short_circuit = any(phrase in critique_lower for phrase in short_circuit_phrases)
        
        if should_short_circuit:
            # Short-circuit: Return proponent's output immediately
            trace.append({
                'step': 'Short-Circuit',
                'message': '✓ Opponent validated the response. Skipping Chairman to save cost/latency.'
            })
            return {
                'final_response': proponent_output,
                'trace': trace,
                'short_circuit': True
            }
        
        # Step 4: Chairman synthesizes final response
        final_response = self.chairman.synthesize(user_query, proponent_output, critique_output, chat_history)
        trace.append({
            'step': 'Chairman',
            'model': self.chairman.model_name,
            'output': final_response
        })
        
        return {
            'final_response': final_response,
            'trace': trace,
            'short_circuit': False
        }


def get_provider_implementation(provider_name: str, api_key: str = None, oauth_credentials=None) -> Optional[LLMProvider]:
    if provider_name == "Ollama":
        return OllamaProvider()
    elif provider_name == "OpenCode" and api_key:
        return OpenAIProvider(api_key)
    elif provider_name == "Claude Code" and api_key:
        return AnthropicProvider(api_key)
    elif provider_name == "Antigravity":
        if api_key:
            return GoogleProvider(api_key=api_key)
        elif oauth_credentials:
            return GoogleProvider(credentials=oauth_credentials)
    elif provider_name == "OpenRouter" and api_key:
        return OpenRouterProvider(api_key)
    return None
