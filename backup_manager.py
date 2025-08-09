#!/usr/bin/env python3
"""
AI Notes Backup Manager
Standalone backup management tool
"""
import sys
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.backup_service import BackupService

def main():
    """Main backup manager interface"""
    parser = argparse.ArgumentParser(
        description="AI Notes Backup Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=        """
Examples:
  python backup_manager.py create                    # Create backup
  python backup_manager.py create --compressed      # Create compressed backup
  python backup_manager.py list                     # List all backups
  python backup_manager.py restore backup_name      # Restore from backup
  python backup_manager.py export --format json     # Export data as JSON
  python backup_manager.py sync --setup             # Setup Google Drive
  python backup_manager.py sync                     # Sync to Google Drive
  python backup_manager.py cleanup --days 30        # Clean old backups
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create backup command
    create_parser = subparsers.add_parser('create', help='Create a new backup')
    create_parser.add_argument('--name', help='Custom backup name')
    create_parser.add_argument('--compressed', action='store_true', help='Create compressed backup')
    
    # List backups command
    list_parser = subparsers.add_parser('list', help='List all backups')
    list_parser.add_argument('--detailed', action='store_true', help='Show detailed information')
    
    # Restore backup command
    restore_parser = subparsers.add_parser('restore', help='Restore from backup')
    restore_parser.add_argument('backup_name', help='Name of backup to restore')
    restore_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    
    # Export data command
    export_parser = subparsers.add_parser('export', help='Export data in various formats')
    export_parser.add_argument('--format', choices=['json', 'csv', 'sql'], default='json', help='Export format')
    export_parser.add_argument('--output', help='Output file path')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync backups to Google Drive')
    sync_parser.add_argument('--setup', action='store_true', help='Setup Google Drive authentication')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean old backups')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Keep backups newer than N days')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show backup status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize backup service
    backup_service = BackupService()
    
    try:
        if args.command == 'create':
            create_backup(backup_service, args)
        elif args.command == 'list':
            list_backups(backup_service, args)
        elif args.command == 'restore':
            restore_backup(backup_service, args)
        elif args.command == 'export':
            export_data(backup_service, args)
        elif args.command == 'sync':
            if args.setup:
                setup_google_drive(backup_service)
            else:
                sync_backups(backup_service, args)
        elif args.command == 'cleanup':
            cleanup_backups(backup_service, args)
        elif args.command == 'status':
            show_status(backup_service)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def create_backup(backup_service, args):
    """Create a new backup"""
    print("🔄 Creating backup...")
    
    if args.compressed:
        backup_path = backup_service.create_compressed_backup(args.name)
        print(f"✅ Compressed backup created: {backup_path}")
    else:
        backup_path = backup_service.create_backup(args.name)
        print(f"✅ Backup created: {backup_path}")

def list_backups(backup_service, args):
    """List all backups"""
    backups = backup_service.list_backups()
    
    if not backups:
        print("📭 No backups found")
        return
    
    print(f"📋 Found {len(backups)} backup(s):")
    print()
    
    for i, backup in enumerate(backups, 1):
        print(f"{i}. {backup['backup_name']}")
        print(f"   📅 Date: {backup['timestamp']}")
        print(f"   📁 Files: {', '.join(backup['files'])}")
        
        if args.detailed:
            print(f"   📊 Size: {backup.get('total_size', 'N/A')} bytes")
            print(f"   🔍 Checksum: {backup.get('checksum', 'N/A')[:8]}...")
            if backup.get('compressed'):
                print(f"   📦 Compressed: Yes")
        
        print()

def restore_backup(backup_service, args):
    """Restore from backup"""
    backups = backup_service.list_backups()
    
    # Find backup by name
    target_backup = None
    for backup in backups:
        if backup['backup_name'] == args.backup_name:
            target_backup = backup
            break
    
    if not target_backup:
        print(f"❌ Backup '{args.backup_name}' not found")
        return
    
    print(f"🔄 Restoring backup: {target_backup['backup_name']}")
    print(f"📅 Date: {target_backup['timestamp']}")
    print(f"📁 Files: {', '.join(target_backup['files'])}")
    
    if not args.force:
        response = input("Continue with restore? (y/N): ")
        if response.lower() != 'y':
            print("❌ Restore cancelled")
            return
    
    # Determine backup path
    if target_backup.get('compressed'):
        backup_path = target_backup['file_path']
    else:
        backup_path = backup_service.backup_dir / target_backup['backup_name']
    
    success = backup_service.restore_backup(backup_path, confirm=False)
    if success:
        print("✅ Restore completed successfully")
    else:
        print("❌ Restore failed")

def export_data(backup_service, args):
    """Export data in various formats"""
    print(f"📤 Exporting data as {args.format.upper()}...")
    
    output_path = backup_service.export_data(args.format, args.output)
    print(f"✅ Data exported to: {output_path}")

def setup_google_drive(backup_service):
    """Setup Google Drive authentication"""
    print("🔧 Setting up Google Drive authentication...")
    
    try:
        success = backup_service.setup_google_drive()
        if success:
            print("✅ Google Drive setup successful!")
            print("🎉 You can now sync backups to Google Drive")
        else:
            print("❌ Google Drive setup failed")
    except Exception as e:
        print(f"❌ Setup error: {str(e)}")

def sync_backups(backup_service, args):
    """Sync backups to Google Drive"""
    print("☁️ Syncing to Google Drive...")
    
    try:
        success = backup_service.sync_to_google_drive()
        if success:
            print("✅ Sync completed successfully")
        else:
            print("❌ Sync failed")
    except Exception as e:
        print(f"❌ Sync error: {str(e)}")

def cleanup_backups(backup_service, args):
    """Clean old backups"""
    print(f"🧹 Cleaning backups older than {args.days} days...")
    
    removed_count = backup_service.cleanup_old_backups(args.days)
    print(f"✅ Removed {removed_count} old backup(s)")

def show_status(backup_service):
    """Show backup status"""
    backups = backup_service.list_backups()
    
    print("📊 Backup Status")
    print("================")
    print(f"Total backups: {len(backups)}")
    
    if backup_service.metadata['last_backup']:
        print(f"Last backup: {backup_service.metadata['last_backup']}")
    else:
        print("Last backup: Never")
    
    print(f"Backup directory: {backup_service.backup_dir}")
    
    if backups:
        latest = backups[0]
        print(f"Latest backup: {latest['backup_name']}")
        print(f"Latest backup date: {latest['timestamp']}")
    
    # Check Google Drive sync status
    print("\n☁️ Google Drive Sync:")
    if backup_service.metadata['google_drive_sync']['enabled']:
        print("✅ Google Drive configured")
        last_sync = backup_service.metadata['google_drive_sync']['last_sync']
        if last_sync:
            print(f"📅 Last sync: {last_sync[:10]}")
        else:
            print("📅 Never synced")
    else:
        print("❌ Google Drive not configured")
        print("💡 Run: python backup_manager.py sync --setup")

if __name__ == "__main__":
    main()
