# Service Account Authentication for Antigravity

**Simplest OAuth method - No consent screen popup!**

## What is a Service Account?

A Service Account is like a "robot user" that can access Google APIs without requiring a human to click "Allow" every time. Perfect for automation and server applications.

## Setup Steps

### 1. Create Service Account
1. Go to [Google Cloud Console - Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Select your project (or create one)
3. Click **"Create Service Account"**
4. Give it a name (e.g., "LLM Council Bot")
5. Click **"Create and Continue"**
6. Skip the optional steps, click **"Done"**

### 2. Download JSON Key
1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **"JSON"**
5. Click **"Create"** - a JSON file will download

### 3. Enable API
1. Go to [APIs & Services](https://console.cloud.google.com/apis/library)
2. Search for **"Generative Language API"**
3. Click **"Enable"**

### 4. Use in App
1. Run `.\run_app.ps1`
2. Select **"Antigravity"**
3. Choose **"Service Account JSON"**
4. Upload the JSON file you downloaded
5. Done! ✅

## Benefits

✅ **No browser popup** - works headlessly  
✅ **No consent screen** - automatic approval  
✅ **Perfect for automation** - can run in scripts  
✅ **More secure** - credentials stored in file, not in code

## Security Note

Keep your Service Account JSON file **private**! It's like a password that gives full access to your Google Cloud project.
