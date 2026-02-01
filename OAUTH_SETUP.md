# Simplified OAuth Setup for Antigravity (Google Gemini)

**No OAuth Consent Screen Required!**

## Quick Setup (3 Steps)

### 1. Install Google Cloud SDK
Download and install from: https://cloud.google.com/sdk/docs/install

### 2. Authenticate
Open PowerShell and run:
```powershell
gcloud auth application-default login
```

This will:
- Open your browser
- Ask you to login with your Google account
- Save credentials locally (no consent screen needed!)

### 3. Use in the App
1. Run `.\run_app.ps1`
2. Select **"Antigravity"**
3. Choose **"Login with Google"**
4. Click **"🔑 Connect with Google Auth"**
5. Done! ✅

## How It Works

This uses **Application Default Credentials (ADC)** which is Google's recommended way for local development. It's much simpler than OAuth consent screens and works immediately.

## Note

You still need a Google Cloud Project with the **Generative Language API** enabled, but you don't need to configure OAuth consent screens or create client IDs.
