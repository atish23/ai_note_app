"""
Backup Service for AI Notes/Task Manager
Handles local and Google Drive backups of app data
"""
import os
import json
import shutil
import sqlite3
import zipfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import subprocess
import tempfile

# Google Drive API imports
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
    import io
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False

class BackupService:
    """Comprehensive backup service for AI Notes app with Google Drive sync"""
    
    def __init__(self, app_dir: Optional[str] = None):
        self.app_dir = Path(app_dir) if app_dir else Path(__file__).parent.parent
        self.backup_dir = self.app_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Google Drive configuration
        self.google_drive_config = {
            'SCOPES': ['https://www.googleapis.com/auth/drive.file'],
            'CREDENTIALS_FILE': self.app_dir / 'google_drive_credentials.json',
            'TOKEN_FILE': self.app_dir / 'google_drive_token.json',
            'FOLDER_NAME': 'AI Notes Backups'
        }
        
        # Data files to backup
        self.data_files = {
            "notes.db": "SQLite database with all notes/tasks",
            "faiss.index": "Vector search index",
            "llm_config.json": "AI provider configuration",
            ".api_key_cache": "Cached API keys"
        }
        
        # Backup metadata
        self.metadata_file = self.backup_dir / "backup_metadata.json"
        self.load_metadata()
    
    def load_metadata(self):
        """Load backup metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {
                "backups": [],
                "last_backup": None,
                "backup_count": 0,
                "google_drive_sync": {
                    "last_sync": None,
                    "folder_id": None,
                    "enabled": False
                }
            }
    
    def save_metadata(self):
        """Save backup metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def create_backup(self, backup_name: Optional[str] = None, 
                     include_metadata: bool = True) -> str:
        """Create a complete backup of all app data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"ai_notes_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup directory
            backup_path.mkdir(exist_ok=True)
            
            # Backup data files
            backed_up_files = []
            for filename, description in self.data_files.items():
                source_path = self.app_dir / filename
                if source_path.exists():
                    dest_path = backup_path / filename
                    shutil.copy2(source_path, dest_path)
                    backed_up_files.append(filename)
            
            # Create backup info
            backup_info = {
                "timestamp": timestamp,
                "backup_name": backup_name,
                "files": backed_up_files,
                "app_version": "1.0.0",
                "total_size": self._get_directory_size(backup_path),
                "checksum": self._calculate_checksum(backup_path)
            }
            
            # Save backup info
            with open(backup_path / "backup_info.json", 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            # Update metadata
            self.metadata["backups"].append(backup_info)
            self.metadata["last_backup"] = timestamp
            self.metadata["backup_count"] += 1
            self.save_metadata()
            
            return str(backup_path)
            
        except Exception as e:
            raise Exception(f"Backup failed: {str(e)}")
    
    def create_compressed_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a compressed backup archive"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = backup_name or f"ai_notes_backup_{timestamp}"
        backup_archive = self.backup_dir / f"{backup_name}.zip"
        
        try:
            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_backup_path = Path(temp_dir) / backup_name
                temp_backup_path.mkdir()
                
                # Copy data files
                for filename in self.data_files.keys():
                    source_path = self.app_dir / filename
                    if source_path.exists():
                        dest_path = temp_backup_path / filename
                        shutil.copy2(source_path, dest_path)
                
                # Create backup info
                backup_info = {
                    "timestamp": timestamp,
                    "backup_name": backup_name,
                    "files": list(self.data_files.keys()),
                    "app_version": "1.0.0",
                    "compressed": True
                }
                
                with open(temp_backup_path / "backup_info.json", 'w') as f:
                    json.dump(backup_info, f, indent=2)
                
                # Create zip archive
                with zipfile.ZipFile(backup_archive, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in temp_backup_path.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(temp_backup_path)
                            zipf.write(file_path, arcname)
                
                return str(backup_archive)
                
        except Exception as e:
            raise Exception(f"Compressed backup failed: {str(e)}")
    
    def restore_backup(self, backup_path: str, confirm: bool = True) -> bool:
        """Restore from a backup"""
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            raise Exception(f"Backup not found: {backup_path}")
        
        try:
            # Check if it's a compressed backup
            if backup_path.suffix == '.zip':
                return self._restore_compressed_backup(backup_path, confirm)
            else:
                return self._restore_directory_backup(backup_path, confirm)
                
        except Exception as e:
            raise Exception(f"Restore failed: {str(e)}")
    
    def _restore_directory_backup(self, backup_path: Path, confirm: bool) -> bool:
        """Restore from directory backup"""
        backup_info_path = backup_path / "backup_info.json"
        
        if not backup_info_path.exists():
            raise Exception("Invalid backup: missing backup_info.json")
        
        with open(backup_info_path, 'r') as f:
            backup_info = json.load(f)
        
        if confirm:
            print(f"Restoring backup: {backup_info['backup_name']}")
            print(f"Timestamp: {backup_info['timestamp']}")
            print(f"Files: {', '.join(backup_info['files'])}")
            
            response = input("Continue with restore? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Restore files
        for filename in backup_info['files']:
            source_path = backup_path / filename
            dest_path = self.app_dir / filename
            
            if source_path.exists():
                # Create backup of current file if it exists
                if dest_path.exists():
                    backup_current = self.app_dir / f"{filename}.backup"
                    shutil.copy2(dest_path, backup_current)
                
                shutil.copy2(source_path, dest_path)
        
        return True
    
    def _restore_compressed_backup(self, backup_path: Path, confirm: bool) -> bool:
        """Restore from compressed backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(temp_path)
            
            # Find backup directory
            backup_dirs = [d for d in temp_path.iterdir() if d.is_dir()]
            if not backup_dirs:
                raise Exception("Invalid compressed backup")
            
            backup_dir = backup_dirs[0]
            return self._restore_directory_backup(backup_dir, confirm)
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        # Check directory backups
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                backup_info_path = backup_dir / "backup_info.json"
                if backup_info_path.exists():
                    with open(backup_info_path, 'r') as f:
                        backup_info = json.load(f)
                    backups.append(backup_info)
        
        # Check compressed backups
        for backup_file in self.backup_dir.glob("*.zip"):
            try:
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Try to read backup info from zip
                    backup_info_files = [f for f in zipf.namelist() if f.endswith('backup_info.json')]
                    if backup_info_files:
                        with zipf.open(backup_info_files[0]) as f:
                            backup_info = json.load(f)
                        backup_info['compressed'] = True
                        backup_info['file_path'] = str(backup_file)
                        backups.append(backup_info)
            except:
                continue
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def export_data(self, format: str = "json", output_path: Optional[str] = None) -> str:
        """Export data in various formats"""
        if format not in ["json", "csv", "sql"]:
            raise Exception(f"Unsupported format: {format}")
        
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.app_dir / f"ai_notes_export_{timestamp}.{format}"
        
        if format == "json":
            return self._export_json(output_path)
        elif format == "csv":
            return self._export_csv(output_path)
        elif format == "sql":
            return self._export_sql(output_path)
    
    def _export_json(self, output_path: str) -> str:
        """Export data as JSON"""
        from .database_service import DatabaseService
        
        db_service = DatabaseService()
        items = db_service.get_all_items()
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_items": len(items),
            "items": [
                {
                    "id": item.id,
                    "timestamp": item.timestamp,
                    "raw_content": item.raw_content,
                    "enhanced_content": item.enhanced_content,
                    "item_type": item.item_type.value,
                    "is_completed": item.is_completed,
                    "formatted_date": item.formatted_date
                }
                for item in items
            ]
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return output_path
    
    def _export_csv(self, output_path: str) -> str:
        """Export data as CSV"""
        import csv
        from .database_service import DatabaseService
        
        db_service = DatabaseService()
        items = db_service.get_all_items()
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Date', 'Type', 'Content', 'Enhanced Content', 'Completed'])
            
            for item in items:
                writer.writerow([
                    item.id,
                    item.formatted_date,
                    item.item_type.value,
                    item.raw_content,
                    item.enhanced_content,
                    item.is_completed
                ])
        
        return output_path
    
    def _export_sql(self, output_path: str) -> str:
        """Export database as SQL"""
        db_path = self.app_dir / "notes.db"
        
        if not db_path.exists():
            raise Exception("Database not found")
        
        # Use sqlite3 to dump database
        result = subprocess.run(
            ["sqlite3", str(db_path), ".dump"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            with open(output_path, 'w') as f:
                f.write(result.stdout)
            return output_path
        else:
            raise Exception(f"SQL export failed: {result.stderr}")
    
    def setup_google_drive(self) -> bool:
        """Setup Google Drive OAuth authentication"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise Exception("Google Drive API not available. Install required packages.")
        
        if not self.google_drive_config['CREDENTIALS_FILE'].exists():
            raise Exception("Google Drive credentials file not found. Please download from Google Cloud Console.")
        
        try:
            # Load existing token
            creds = None
            if self.google_drive_config['TOKEN_FILE'].exists():
                creds = Credentials.from_authorized_user_file(
                    str(self.google_drive_config['TOKEN_FILE']), 
                    self.google_drive_config['SCOPES']
                )
            
            # If no valid credentials, let user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.google_drive_config['CREDENTIALS_FILE']), 
                        self.google_drive_config['SCOPES']
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.google_drive_config['TOKEN_FILE'], 'w') as token:
                    token.write(creds.to_json())
            
            # Test connection
            service = build('drive', 'v3', credentials=creds)
            
            # Create or find backup folder
            folder_id = self._get_or_create_backup_folder(service)
            
            # Update metadata
            self.metadata['google_drive_sync']['enabled'] = True
            self.metadata['google_drive_sync']['folder_id'] = folder_id
            self.save_metadata()
            
            return True
            
        except Exception as e:
            raise Exception(f"Google Drive setup failed: {str(e)}")
    
    def _get_or_create_backup_folder(self, service) -> str:
        """Get or create the backup folder in Google Drive"""
        folder_name = self.google_drive_config['FOLDER_NAME']
        
        # Search for existing folder
        results = service.files().list(
            q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        if results['files']:
            return results['files'][0]['id']
        
        # Create new folder
        folder_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = service.files().create(
            body=folder_metadata,
            fields='id'
        ).execute()
        
        return folder['id']
    
    def sync_to_google_drive(self) -> bool:
        """Sync latest backup to Google Drive"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise Exception("Google Drive API not available")
        
        if not self.metadata['google_drive_sync']['enabled']:
            raise Exception("Google Drive not set up. Run setup_google_drive() first.")
        
        try:
            # Load credentials
            creds = Credentials.from_authorized_user_file(
                str(self.google_drive_config['TOKEN_FILE']), 
                self.google_drive_config['SCOPES']
            )
            
            service = build('drive', 'v3', credentials=creds)
            folder_id = self.metadata['google_drive_sync']['folder_id']
            
            # Create latest backup
            backup_path = self.create_compressed_backup()
            backup_file = Path(backup_path)
            
            # Upload to Google Drive
            file_metadata = {
                'name': backup_file.name,
                'parents': [folder_id]
            }
            
            media = MediaFileUpload(
                str(backup_file), 
                mimetype='application/zip',
                resumable=True
            )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Update metadata
            self.metadata['google_drive_sync']['last_sync'] = datetime.now().isoformat()
            self.save_metadata()
            
            return True
            
        except Exception as e:
            raise Exception(f"Google Drive sync failed: {str(e)}")
    
    def list_google_drive_backups(self) -> List[Dict]:
        """List backups available in Google Drive"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise Exception("Google Drive API not available")
        
        if not self.metadata['google_drive_sync']['enabled']:
            raise Exception("Google Drive not set up")
        
        try:
            creds = Credentials.from_authorized_user_file(
                str(self.google_drive_config['TOKEN_FILE']), 
                self.google_drive_config['SCOPES']
            )
            
            service = build('drive', 'v3', credentials=creds)
            folder_id = self.metadata['google_drive_sync']['folder_id']
            
            # List files in backup folder
            results = service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                fields='files(id, name, createdTime, size)',
                orderBy='createdTime desc'
            ).execute()
            
            return results['files']
            
        except Exception as e:
            raise Exception(f"Failed to list Google Drive backups: {str(e)}")
    
    def download_from_google_drive(self, file_id: str, local_path: str) -> bool:
        """Download a backup file from Google Drive"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise Exception("Google Drive API not available")
        
        try:
            creds = Credentials.from_authorized_user_file(
                str(self.google_drive_config['TOKEN_FILE']), 
                self.google_drive_config['SCOPES']
            )
            
            service = build('drive', 'v3', credentials=creds)
            
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Save to local file
            with open(local_path, 'wb') as f:
                f.write(fh.getvalue())
            
            return True
            
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")
    
    def _get_latest_backup(self) -> Optional[Path]:
        """Get the most recent backup file"""
        backups = self.list_backups()
        if backups:
            latest = backups[0]
            if latest.get('compressed'):
                return Path(latest['file_path'])
            else:
                return self.backup_dir / latest['backup_name']
        return None
    
    def _get_directory_size(self, path: Path) -> int:
        """Calculate directory size in bytes"""
        total_size = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size
    
    def _calculate_checksum(self, path: Path) -> str:
        """Calculate checksum of backup directory"""
        hasher = hashlib.sha256()
        
        for file_path in sorted(path.rglob('*')):
            if file_path.is_file():
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
        
        return hasher.hexdigest()
    
    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """Remove backups older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        for backup in self.list_backups():
            backup_date = datetime.strptime(backup['timestamp'], "%Y%m%d_%H%M%S")
            if backup_date < cutoff_date:
                if backup.get('compressed'):
                    backup_path = Path(backup['file_path'])
                else:
                    backup_path = self.backup_dir / backup['backup_name']
                
                if backup_path.exists():
                    if backup_path.is_file():
                        backup_path.unlink()
                    else:
                        shutil.rmtree(backup_path)
                    removed_count += 1
        
        return removed_count
