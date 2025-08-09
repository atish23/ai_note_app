"""
Database service for notes management
"""
import sqlite3
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import NoteItem, ItemType

class DatabaseService:
    """Central database service for all database operations"""
    
    def __init__(self, db_path: str = "notes.db"):
        self.db_path = Path(db_path)
        self._init_database()
    
    def initialize(self):
        """Initialize database and create tables if needed"""
        self._init_database()
    
    def _init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Create notes table
            conn.execute(
                """CREATE TABLE IF NOT EXISTS notes
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts REAL,
                    raw TEXT,
                    enhanced TEXT,
                    item_type TEXT DEFAULT 'note',
                    is_completed INTEGER DEFAULT 0)"""
            )
            
            # Create user context table
            conn.execute(
                """CREATE TABLE IF NOT EXISTS user_context
                   (key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_ts REAL)"""
            )
            
            # Add item_type column if it doesn't exist (migration)
            try:
                conn.execute("ALTER TABLE notes ADD COLUMN item_type TEXT DEFAULT 'note'")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            # Add is_completed column if it doesn't exist (migration)
            try:
                conn.execute("ALTER TABLE notes ADD COLUMN is_completed INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            conn.commit()
        finally:
            conn.close()
    
    def create_item(self, item: NoteItem) -> int:
        """Create a new item and return its ID"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """INSERT INTO notes (ts, raw, enhanced, item_type, is_completed) 
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    item.timestamp,
                    item.raw_content,
                    item.enhanced_content,
                    item.item_type.value,
                    int(item.is_completed)
                )
            )
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def get_item(self, item_id: int) -> Optional[NoteItem]:
        """Get item by ID"""
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                """SELECT id, ts, raw, enhanced, 
                          COALESCE(item_type, 'note') as item_type,
                          COALESCE(is_completed, 0) as is_completed
                   FROM notes WHERE id = ?""",
                (item_id,)
            ).fetchone()
            
            if row:
                return NoteItem(
                    id=row[0],
                    timestamp=row[1],
                    raw_content=row[2],
                    enhanced_content=row[3],
                    item_type=ItemType(row[4]),
                    is_completed=bool(row[5])
                )
            return None
        finally:
            conn.close()
    
    def get_all_items(self, 
                     item_type: Optional[ItemType] = None,
                     include_completed: bool = True) -> List[NoteItem]:
        """Get all items with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        try:
            query = """SELECT id, ts, raw, enhanced, 
                             COALESCE(item_type, 'note') as item_type,
                             COALESCE(is_completed, 0) as is_completed
                       FROM notes"""
            params = []
            
            conditions = []
            if item_type:
                conditions.append("item_type = ?")
                params.append(item_type.value)
            
            if not include_completed:
                conditions.append("is_completed = 0")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY ts DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            items = []
            for row in rows:
                items.append(NoteItem(
                    id=row[0],
                    timestamp=row[1],
                    raw_content=row[2],
                    enhanced_content=row[3],
                    item_type=ItemType(row[4]),
                    is_completed=bool(row[5])
                ))
            
            return items
        finally:
            conn.close()
    
    def update_item(self, item: NoteItem) -> bool:
        """Update an existing item"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                """UPDATE notes SET raw = ?, enhanced = ?, item_type = ?, 
                   is_completed = ?
                   WHERE id = ?""",
                (
                    item.raw_content,
                    item.enhanced_content,
                    item.item_type.value,
                    int(item.is_completed),
                    item.id
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def update_completion_status(self, item_id: int, is_completed: bool) -> bool:
        """Update completion status of an item"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "UPDATE notes SET is_completed = ? WHERE id = ?",
                (int(is_completed), item_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def update_item_content(self, item_id: int, raw_content: str, enhanced_content: str) -> bool:
        """Update the content of an item"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute(
                "UPDATE notes SET raw = ?, enhanced = ? WHERE id = ?",
                (raw_content, enhanced_content, item_id)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_item(self, item_id: int) -> bool:
        """Delete an item by ID"""
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.execute("DELETE FROM notes WHERE id = ?", (item_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def search_items(self, query: str, limit: int = 50) -> List[NoteItem]:
        """Basic text search in items"""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                """SELECT id, ts, raw, enhanced, 
                          COALESCE(item_type, 'note') as item_type,
                          COALESCE(is_completed, 0) as is_completed
                   FROM notes 
                   WHERE raw LIKE ? OR enhanced LIKE ?
                   ORDER BY ts DESC
                   LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit)
            ).fetchall()
            
            items = []
            for row in rows:
                items.append(NoteItem(
                    id=row[0],
                    timestamp=row[1],
                    raw_content=row[2],
                    enhanced_content=row[3],
                    item_type=ItemType(row[4]),
                    is_completed=bool(row[5])
                ))
            
            return items
        finally:
            conn.close()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        try:
            # Total count
            total = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
            
            # By type
            type_stats = conn.execute(
                """SELECT item_type, COUNT(*) 
                   FROM notes 
                   GROUP BY item_type"""
            ).fetchall()
            
            # Completion stats
            completion_stats = conn.execute(
                """SELECT is_completed, COUNT(*) 
                   FROM notes 
                   WHERE item_type = 'task'
                   GROUP BY is_completed"""
            ).fetchall()
            
            stats = {
                "total_items": total,
                "by_type": dict(type_stats),
                "completion": dict(completion_stats)
            }
            
            return stats
        finally:
            conn.close()
    
    # Context management methods
    def save_context(self, key: str, value: str):
        """Save user context"""
        conn = sqlite3.connect(self.db_path)
        try:
            conn.execute(
                """INSERT OR REPLACE INTO user_context (key, value, updated_ts)
                   VALUES (?, ?, ?)""",
                (key, value, time.time())
            )
            conn.commit()
        finally:
            conn.close()
    
    def get_context(self, key: str) -> Optional[str]:
        """Get user context"""
        conn = sqlite3.connect(self.db_path)
        try:
            row = conn.execute(
                "SELECT value FROM user_context WHERE key = ?",
                (key,)
            ).fetchone()
            return row[0] if row else None
        finally:
            conn.close()
    
    def get_all_context(self) -> Dict[str, str]:
        """Get all user context"""
        conn = sqlite3.connect(self.db_path)
        try:
            rows = conn.execute(
                "SELECT key, value FROM user_context ORDER BY updated_ts DESC"
            ).fetchall()
            return dict(rows)
        finally:
            conn.close()
