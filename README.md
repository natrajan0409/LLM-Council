# 🏛️ LLM Council

A powerful "Council of LLMs" application where multiple AI models deliberate on queries, with a debate-style architecture that optimizes for both quality and cost efficiency.

## 🚀 Features

### Core Features
*   **Multi-Provider Support**: Choose from **Ollama** (local), **Claude Code**, **OpenCode** (OpenAI), **Antigravity** (Gemini), or **OpenRouter**
*   **Two Council Modes**:
    *   **Classic Council**: 2-3 models deliberate, Chairman synthesizes (original behavior)
    *   **Debate Council**: Proponent → Opponent (Logic Auditor) → Chairman with intelligent short-circuit ⚡
*   **Smart Cost Optimization**: Debate mode saves 33% on API calls when initial response is accurate
*   **Transparency**: View complete chain of thought showing how the council reached its decision
*   **Context Aware**: Maintains conversation history for coherent multi-turn discussions
*   **Local & Cloud**: Seamless switching between offline (Ollama) and cloud APIs

### Performance Optimizations 🚄
*   **Optimized for Local Models**: 60-70% faster responses with Ollama
*   **Configurable Parameters**: Tune context window, response length, and sampling
*   **Recommended Fast Models**: `llama3.2:3b`, `phi3:mini`, `qwen2.5:3b`
*   **Expected Speed**: 2-5 seconds per query (with optimizations)

### Bonus Tools 🛠️
*   **Excel Comparator**: Java utility to compare two Excel files and show differences in console
*   **Performance Config**: Tunable settings for speed vs quality trade-offs

## 📋 Prerequisites

### 1. Ollama (Local/Offline) - Recommended for Speed
- Install [Ollama](https://ollama.com/)
- Pull optimized models for fast responses:
  ```bash
  ollama pull llama3.2:3b    # Fast & efficient
  ollama pull phi3:mini      # Very fast
  ollama pull qwen2.5:3b     # Fast & high quality
  ```
- Or pull standard models:
  ```bash
  ollama pull llama3:8b
  ollama pull mistral:7b
  ```

### 2. Cloud APIs (Optional)
- **Claude Code**: Requires Anthropic API Key ([Get Key](https://console.anthropic.com/))
- **OpenCode**: Requires OpenAI API Key ([Get Key](https://platform.openai.com/api-keys))
- **Antigravity**: Requires Google Gemini API Key ([Get Key](https://aistudio.google.com/app/apikey))
- **OpenRouter**: Requires OpenRouter API Key ([Get Key](https://openrouter.ai/keys))

## 🛠️ Installation & Running

### Python LLM Council

This project uses **uv** for fast dependency management.

```powershell
# Option 1: Use the run script
.\run_app.ps1

# Option 2: Use uv directly
uv run streamlit run main.py
```

The app will open at: http://localhost:8501

### Java Excel Comparator (Optional)

```bash
# Build the tool
mvn clean package

# Run comparison
java -jar target/excel-comparator-1.0.0-jar-with-dependencies.jar file1.xlsx file2.xlsx
```

See [EXCEL_COMPARATOR_README.md](EXCEL_COMPARATOR_README.md) for details.

## 🧩 How to Use

### Quick Start
1.  **Launch**: Run `uv run streamlit run main.py`
2.  **Select Provider**: Choose your AI provider (Ollama recommended for speed)
3.  **Connect**: Click "Connect & Fetch Models"
4.  **Select Council Mode**: Choose between Classic or Debate Council
5.  **Configure Models**: 
    - **Classic**: Select Chairman + 2-3 Council Members
    - **Debate**: Select Proponent, Opponent, Chairman
6.  **Chat**: Ask your question and watch the deliberation!

### Council Modes Explained

#### Classic Council Mode
- 2-3 models provide independent opinions
- Chairman synthesizes all perspectives
- **Best for**: Complex topics needing multiple viewpoints
- **API Calls**: 3-4 per query

#### Debate Council Mode ⚡ (Recommended)
- **Step 1**: Proponent generates initial draft
- **Step 2**: Opponent (Logic Auditor) critiques for flaws
- **Step 3**: Short-circuit if no flaws found (saves 33%!)
- **Step 4**: Chairman synthesizes final response (only if needed)
- **Best for**: General queries, factual questions, cost optimization
- **API Calls**: 2-3 per query (2 with short-circuit)

## 📊 Performance Optimization

For faster responses with local models, see [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)

**Quick Tips:**
- Use small models (3B parameters) for 3-5 second responses
- Use Debate Council mode for 33% cost savings
- Enable speed optimizations (already active by default)
- Configure settings in `performance_config.ini`

## 📚 Documentation

- [walkthrough.txt](walkthrough.txt) - Complete feature walkthrough with flowchart
- [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md) - Speed optimization guide
- [EXCEL_COMPARATOR_README.md](EXCEL_COMPARATOR_README.md) - Excel comparison tool
- [OAUTH_SETUP.md](OAUTH_SETUP.md) - OAuth authentication setup
- [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md) - Service account setup

## 🎯 Use Cases

### Fast Factual Queries
- **Mode**: Debate Council
- **Model**: `llama3.2:3b`
- **Speed**: 2-4 seconds
- **Example**: "What is the capital of France?"

### Complex Analysis
- **Mode**: Classic Council
- **Model**: `llama3:8b` or `mistral:7b`
- **Speed**: 10-15 seconds
- **Example**: "Should I use microservices for a small startup?"

### Cost-Sensitive Queries
- **Mode**: Debate Council
- **Provider**: Ollama (free, local)
- **Savings**: 33% with short-circuit

## 🔧 Configuration Files

- `pyproject.toml` - Python dependencies
- `performance_config.ini` - Performance tuning
- `pom.xml` - Java Excel Comparator dependencies
- `.gitignore` - Excluded files

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional AI providers
- Streaming responses
- Multi-round debates
- Performance metrics dashboard

## 📝 License

This is a proof-of-concept project. Use at your own discretion.

## 🐛 Troubleshooting

**Slow responses?**
- Switch to smaller model (3B instead of 7B+)
- Use Debate Council mode
- See [PERFORMANCE_OPTIMIZATION.md](PERFORMANCE_OPTIMIZATION.md)

**Authentication issues?**
- See [OAUTH_SETUP.md](OAUTH_SETUP.md)
- See [SERVICE_ACCOUNT_SETUP.md](SERVICE_ACCOUNT_SETUP.md)

**Excel Comparator not working?**
- Ensure Java 11+ is installed
- Run `mvn clean package` first
- See [EXCEL_COMPARATOR_README.md](EXCEL_COMPARATOR_README.md)

## 🌟 Highlights

✅ **60-70% faster** local model responses with optimizations  
✅ **33% cost savings** with Debate Council short-circuit  
✅ **Complete transparency** with chain of thought visualization  
✅ **Multi-provider** support (Ollama, Claude, OpenAI, Gemini)  
✅ **Bonus tools** including Excel file comparison utility  

---

**Built with**: Python, Streamlit, Ollama, Apache POI  
**Optimized for**: Speed, Cost Efficiency, Transparency
