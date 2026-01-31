# 🏛️ LLM Council POC

A "Council of LLMs" application where multiple AI models deliberated on a user's query, and a "Chairman" model synthesizes their opinions into a final, high-quality response.

## 🚀 Features

*   **Multi-Provider Support**: Choose from **Ollama**, **Claude Code**, **OpenCode** (OpenAI), or **Antigravity** (Gemini).
*   **Council Deliberation**: Select 2-3 unique models to act as council members.
*   **Chairman Synthesis**: A designated "Chairman" model reviews the council's output and provides the final answer.
*   **Context Aware**: Maintains conversation history.
*   **Local & Cloud**: seamless switching between offline (Ollama) and cloud APIs.

## 📋 Prerequisites

### 1. Ollama (Offline)
- Install [Ollama](https://ollama.com/).
- Pull models: `ollama pull llama3`, `ollama pull mistral`

### 2. Cloud APIs (Optional)
- **Claude Code**: Requires Anthropic API Key.
- **OpenCode**: Requires OpenAI API Key.
- **Antigravity**: Requires Google Gemini API Key.

## 🛠️ Installation & Running

This project uses **uv** for fast and easy dependency management.

```powershell
.\run_app.ps1
```

## 🧩 Architecture

1.  **Select Tool**: Choose your provider (e.g., Ollama or Claude).
2.  **Authenticate**: Enter API Key if using a cloud provider.
3.  **Configure**: Select Models for the Council and Chairman.
4.  **Chat**: The models deliberate and synthesize a response.
