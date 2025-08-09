#!/usr/bin/env python3
"""
Google Drive Setup for AI Notes Backup
Helps users set up Google Drive OAuth authentication
"""
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.backup_service import BackupService

def main():
    """Setup Google Drive authentication"""
    print("🔧 Google Drive Setup for AI Notes")
    print("==================================")
    print()
    
    backup_service = BackupService()
    
    # Check if credentials file exists
    credentials_file = backup_service.google_drive_config['CREDENTIALS_FILE']
    
    if not credentials_file.exists():
        print("❌ Google Drive credentials file not found!")
        print()
        print("📋 To set up Google Drive backup:")
        print("1. Go to Google Cloud Console: https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create OAuth 2.0 credentials")
        print("5. Download credentials as JSON")
        print("6. Save as 'google_drive_credentials.json' in this folder")
        print()
        print("📁 Expected file: google_drive_credentials.json")
        print("📁 Current directory:", Path.cwd())
        print()
        return False
    
    print("✅ Credentials file found!")
    print()
    
    try:
        print("🔄 Setting up Google Drive authentication...")
        print("This will open your browser for OAuth login.")
        print()
        
        success = backup_service.setup_google_drive()
        
        if success:
            print("✅ Google Drive setup successful!")
            print()
            print("🎉 Your AI Notes app can now sync to Google Drive!")
            print("📱 Use the 'Sync to Google Drive' button in the app.")
            print()
            print("📊 Backup folder: 'AI Notes Backups' in your Google Drive")
            return True
        else:
            print("❌ Google Drive setup failed")
            return False
            
    except Exception as e:
        print(f"❌ Setup error: {str(e)}")
        print()
        print("💡 Troubleshooting:")
        print("- Make sure you have internet connection")
        print("- Check that credentials file is valid")
        print("- Try running setup again")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
