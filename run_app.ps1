Write-Host "Checking for Ollama..." -ForegroundColor Cyan

# Check if "ollama" command exists
if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Error: Ollama is not installed!" -ForegroundColor Red
    Write-Host "Please install Ollama from https://ollama.com" -ForegroundColor Yellow
    exit 1
}

# Try to list models to verify if the server is running
$ollamaProcess = Start-Process -FilePath "ollama" -ArgumentList "list" -NoNewWindow -PassThru -Wait

if ($ollamaProcess.ExitCode -ne 0) {
    Write-Host "⚠️  Ollama server is not running." -ForegroundColor Yellow
    Write-Host "🔄 Attempting to start Ollama server..." -ForegroundColor Cyan
    
    # Start Ollama serve in the background
    try {
        Start-Process -FilePath "ollama" -ArgumentList "serve" -NoNewWindow
        
        # Give it a few seconds to initialize
        Write-Host "⏳ Waiting for Ollama to initialize (5s)..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 5
        
        # Verify again
        $retryProcess = Start-Process -FilePath "ollama" -ArgumentList "list" -NoNewWindow -PassThru -Wait
        if ($retryProcess.ExitCode -eq 0) {
            Write-Host "✅ Ollama started successfully." -ForegroundColor Green
        }
        else {
            Write-Host "❌ Failed to auto-start Ollama." -ForegroundColor Red
            Write-Host "Please start 'ollama serve' manually in another terminal." -ForegroundColor Yellow
            exit 1
        }
    }
    catch {
        Write-Host "❌ Failed to launch Ollama process." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "✅ Ollama is already running." -ForegroundColor Green
}

Write-Host "🚀 Starting LLM Council..." -ForegroundColor Cyan
uv run streamlit run main.py
