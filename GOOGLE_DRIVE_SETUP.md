# Google Drive Backup Setup - Complete Guide

This guide provides detailed step-by-step instructions for setting up Google Drive backup for your AI Notes app.

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter project name: `AI Notes Backup`
   - Click "Create"

3. **Select Your Project**
   - Make sure your new project is selected in the dropdown

### Step 2: Enable Google Drive API

1. **Go to APIs & Services**
   - In the left sidebar, click "APIs & Services"
   - Click "Library"

2. **Search for Google Drive API**
   - In the search box, type "Google Drive API"
   - Click on "Google Drive API" from results

3. **Enable the API**
   - Click "Enable" button
   - Wait for confirmation

### Step 3: Create OAuth 2.0 Credentials

1. **Go to Credentials**
   - In the left sidebar, click "APIs & Services"
   - Click "Credentials"

2. **Create Credentials**
   - Click "Create Credentials" button
   - Select "OAuth client ID"

3. **Configure OAuth Consent Screen**
   - If prompted, click "Configure Consent Screen"
   - Choose "External" user type
   - Click "Create"

4. **Fill in App Information**
   - **App name**: `AI Notes Backup`
   - **User support email**: Your email
   - **Developer contact information**: Your email
   - Click "Save and Continue"

5. **Add Scopes**
   - Click "Add or Remove Scopes"
   - Search for "Google Drive API"
   - Select `https://www.googleapis.com/auth/drive.file`
   - Click "Update"
   - Click "Save and Continue"

6. **Add Test Users**
   - Click "Add Users"
   - Add your email address
   - Click "Save and Continue"
   - Click "Back to Dashboard"

7. **Create OAuth Client ID**
   - Go back to "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - **Application type**: Desktop application
   - **Name**: `AI Notes Desktop Client`
   - Click "Create"

8. **Download Credentials**
   - Click "Download JSON"
   - Save the file as `google_drive_credentials.json`
   - Place it in your AI Notes app folder

### Step 4: Verify Credentials

1. **Check File Location**
   ```bash
   # Make sure the file is in your app directory
   ls -la google_drive_credentials.json
   ```

2. **Verify File Format**
   ```bash
   python verify_credentials.py
   ```

   You should see:
   ```
   ✅ Credentials file looks valid!
   📁 Project ID: your-project-id
   🔑 Client ID: 123456789-abc...
   🎉 You can now run: python setup_google_drive.py
   ```

### Step 5: Setup Google Drive Authentication

1. **Run Setup Script**
   ```bash
   python setup_google_drive.py
   ```

2. **Complete OAuth Flow**
   - A browser window will open
   - Sign in with your Google account
   - Click "Advanced" → "Go to AI Notes Backup (unsafe)"
   - Click "Allow"
   - You'll see a success message

3. **Verify Setup**
   ```bash
   python backup_manager.py status
   ```

   You should see:
   ```
   ☁️ Google Drive Sync:
   ✅ Google Drive configured
   📅 Never synced
   ```

### Step 6: Test Backup and Sync

1. **Create a Test Backup**
   ```bash
   python backup_manager.py create --compressed
   ```

2. **Sync to Google Drive**
   ```bash
   python backup_manager.py sync
   ```

3. **Check Google Drive**
   - Go to https://drive.google.com/
   - Look for folder "AI Notes Backups"
   - You should see your backup file

## 📱 Using in the App

### Sync from App UI
1. Open AI Notes app
2. Look for "☁️ Backup & Sync" in the sidebar
3. Click "🔄 Sync to Google Drive"
4. Wait for sync to complete

### Check Sync Status
- The app shows "Last sync" date in sidebar
- Green checkmark when sync is successful
- Error messages if something goes wrong

## 🔒 Security Information

### What's Protected
- **Credentials file** - Never committed to git
- **OAuth tokens** - Stored locally only
- **Backup files** - Private to your Google Drive
- **Your data** - Only you can access

### What Gets Backed Up
- `notes.db` - All your notes, tasks, resources
- `faiss.index` - Vector search index
- `llm_config.json` - AI provider configuration
- `.api_key_cache` - Cached API keys

### Backup Format
- **Compressed ZIP** - Efficient storage
- **LLM-Compatible** - Can be imported by AI systems
- **Metadata Included** - Timestamps, checksums
- **Complete Backup** - All app data included

## 🔧 Troubleshooting

### "Credentials file not found"
```bash
# Check if file exists
ls -la google_drive_credentials.json

# If missing, download from Google Cloud Console
# Save as google_drive_credentials.json in app folder
```

### "Invalid credentials format"
```bash
# Verify credentials
python verify_credentials.py

# Check file structure matches template
cat google_drive_credentials_template.json
```

### "Authentication failed"
```bash
# Delete old token and try again
rm google_drive_token.json
python setup_google_drive.py
```

### "API not enabled"
1. Go to Google Cloud Console
2. Select your project
3. Go to "APIs & Services" → "Library"
4. Search for "Google Drive API"
5. Click "Enable"

### "OAuth consent screen not configured"
1. Go to Google Cloud Console
2. "APIs & Services" → "OAuth consent screen"
3. Fill in required information
4. Add your email as test user
5. Save and continue

## 📊 Command Reference

### Setup Commands
```bash
# Verify credentials
python verify_credentials.py

# Setup Google Drive
python setup_google_drive.py

# Check status
python backup_manager.py status
```

### Backup Commands
```bash
# Create backup
python backup_manager.py create --compressed

# Sync to Google Drive
python backup_manager.py sync

# List backups
python backup_manager.py list

# Export data
python backup_manager.py export --format json
```

### Restore Commands
```bash
# List available backups
python backup_manager.py list

# Restore from backup
python backup_manager.py restore backup_name

# Export data for LLM
python backup_manager.py export --format json
```

## 🎯 Advanced Features

### Automatic Backup Scheduling
```bash
# Add to crontab for daily backups
0 2 * * * cd /path/to/ai_notes && python backup_manager.py sync
```

### Multiple Export Formats
```bash
# JSON format (for LLMs)
python backup_manager.py export --format json

# CSV format (for spreadsheets)
python backup_manager.py export --format csv

# SQL format (for databases)
python backup_manager.py export --format sql
```

### Cleanup Old Backups
```bash
# Remove backups older than 30 days
python backup_manager.py cleanup --days 30
```

## 🎉 Success!

Once set up, your AI Notes data will be:
- ✅ **Automatically backed up** to Google Drive
- ✅ **Securely stored** with OAuth authentication
- ✅ **LLM-compatible** for AI system integration
- ✅ **Easy to restore** from any backup
- ✅ **Private and secure** - only you can access

Your data is now safely backed up to Google Drive! 🛡️✨
