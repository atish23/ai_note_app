"""
AI Notes/Task Manager - Redesigned with Better UX
"""
import streamlit as st
import time
from typing import Optional

# Import shared agent service
from core.agent_service import NotesAgentService
from core.models import ItemType

# ---------- CONFIG ----------------------------------------------------------
st.set_page_config(
    page_title="AI Notes",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE ---------------------------------------------------

def init_session_state():
    """Initialize session state"""
    if 'agent' not in st.session_state:
        st.session_state.agent = NotesAgentService()
        
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
        
    if 'current_view' not in st.session_state:
        st.session_state.current_view = "tasks"  # Default to tasks view

# ---------- UI FUNCTIONS ----------------------------------------------------

def show_setup_page():
    """Show API key setup page"""
    st.title("🧠 AI Notes")
    st.subheader("⚙️ Setup Required")
    
    # LLM Provider Selection - Always show this first
    st.info("Choose your AI provider:")
    
    # Get available providers
    available_providers = st.session_state.agent.ai_service.get_available_providers()
    current_provider = st.session_state.agent.ai_service.get_current_provider()
    
    # Provider selection
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_provider = st.selectbox(
            "AI Provider:",
            available_providers,
            index=available_providers.index(current_provider) if current_provider in available_providers else 0,
            help="Choose between cloud AI (Gemini) or local AI (Ollama)"
        )
        
        if selected_provider != current_provider:
            if st.button("Switch Provider"):
                with st.spinner("Switching provider..."):
                    success = st.session_state.agent.ai_service.switch_provider(selected_provider)
                    if success:
                        st.success(f"Switched to {selected_provider}!")
                        st.rerun()
                    else:
                        st.error(f"Failed to switch to {selected_provider}")
    
    with col2:
        if selected_provider == "gemini":
            st.info("**Gemini (Google AI)**\n- Cloud-based\n- Requires API key\n- High quality responses\n- Usage limits/costs")
        elif selected_provider == "ollama":
            st.info("**Ollama (Local)**\n- Runs locally\n- No API key needed\n- Free to use\n- Requires Ollama installed")
    
    st.divider()
    
    # Provider-specific setup based on CURRENT provider (after any switch)
    current_provider = st.session_state.agent.ai_service.get_current_provider()
    
    if current_provider == "gemini":
        # Check for cached key
        api_key = st.session_state.agent.ai_service.get_api_key()
        if api_key:
            st.success("✅ Gemini API key found in cache!")
            if st.button("Continue with Gemini"):
                try:
                    with st.spinner("Initializing..."):
                        if st.session_state.agent.initialize():
                            st.session_state.initialized = True
                            st.rerun()
                        else:
                            st.error("Failed to initialize. Please check your API key.")
                            st.info("Debug: Try refreshing the page or re-entering your API key.")
                except Exception as e:
                    st.error(f"Initialization error: {str(e)}")
                    st.info("Please refresh the page and try again.")
        else:
            # API key input
            st.subheader("🔑 Enter Gemini API Key")
            st.info("Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
            
            api_key = st.text_input(
                "API Key:",
                type="password",
                placeholder="sk-...",
                help="Your Gemini API key"
            )
            
            if st.button("Save & Continue", type="primary"):
                if api_key:
                    with st.spinner("Saving and initializing..."):
                        st.session_state.agent.ai_service.save_api_key(api_key)
                        if st.session_state.agent.initialize():
                            st.session_state.initialized = True
                            st.success("✅ Setup complete!")
                            st.rerun()
                        else:
                            st.error("Failed to initialize. Please check your API key.")
                else:
                    st.error("Please enter your API key.")
    
    elif current_provider == "ollama":
        st.subheader("🦙 Ollama Setup")
        st.info("Make sure Ollama is installed and running: https://ollama.ai")
        
        if st.button("Test Ollama Connection"):
            with st.spinner("Testing Ollama..."):
                if st.session_state.agent.initialize():
                    st.session_state.initialized = True
                    st.success("✅ Ollama connected!")
                    st.rerun()
                else:
                    st.error("❌ Ollama not found. Please install and start Ollama.")
                    st.info("Run: `ollama serve` in terminal")

def show_navigation():
    """Show clean navigation bar"""
    st.markdown("---")
    
    # Navigation tabs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        if st.button("📋 Tasks", use_container_width=True, type="primary" if st.session_state.current_view == "tasks" else "secondary"):
            st.session_state.current_view = "tasks"
            st.rerun()
    
    with col2:
        if st.button("📝 Notes", use_container_width=True, type="primary" if st.session_state.current_view == "notes" else "secondary"):
            st.session_state.current_view = "notes"
            st.rerun()
    
    with col3:
        if st.button("🔗 Resources", use_container_width=True, type="primary" if st.session_state.current_view == "resources" else "secondary"):
            st.session_state.current_view = "resources"
            st.rerun()
    
    with col4:
        if st.button("🔍 Search", use_container_width=True, type="primary" if st.session_state.current_view == "search" else "secondary"):
            st.session_state.current_view = "search"
            st.rerun()
    
    with col5:
        if st.button("📊 All Items", use_container_width=True, type="primary" if st.session_state.current_view == "all" else "secondary"):
            st.session_state.current_view = "all"
            st.rerun()
    
    with col6:
        if st.button("☁️ Backup", use_container_width=True, type="primary" if st.session_state.current_view == "backup" else "secondary"):
            st.session_state.current_view = "backup"
            st.rerun()

def show_smart_input():
    """Show the main smart input box"""
    st.markdown("### ✨ Smart Input")
    
    # Helpful tips
    with st.expander("💡 Tips for better task detection"):
        st.markdown("""
        **To ensure items are detected as tasks, use words like:**
        - "need to", "have to", "should", "must"
        - "buy", "get", "find", "check", "call"
        - "finish", "complete", "start", "work on"
        - "meeting", "deadline", "due by"
        
        **Or force the type with:**
        - `@task` - Force as task
        - `@note` - Force as note  
        - `@resource` - Force as resource
        
        **Examples:**
        - "I need to buy groceries" → Task
        - "Call mom tomorrow" → Task
        - "@task Meeting notes from today" → Task
        """)
    
    # Smart input form
    with st.form("smart_input", clear_on_submit=True):
        content = st.text_input(
            "Add item:",
            placeholder="I need to finish the report by Friday",
            help="Type anything - AI will detect if it's a task, note, or resource"
        )
        
        submitted = st.form_submit_button("✨ Add Item", type="primary", use_container_width=True)
        
        if submitted and content.strip():
            with st.spinner("Processing..."):
                result = st.session_state.agent.create_item(content.strip())
                
                if result.success:
                    item = result.data
                    type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
                    
                    # Show enhanced content if available
                    enhanced = getattr(item, 'enhanced_content', None)
                    if enhanced and enhanced != content.strip():
                        st.success(f"{type_emoji} Added {item.item_type.value}!")
                        with st.expander("✨ AI Enhanced Version", expanded=True):
                            st.write(enhanced)
                    else:
                        st.success(f"{type_emoji} Added {item.item_type.value}!")
                    
                    st.rerun()
                else:
                    st.error(f"Error: {result.message}")

def show_tasks_view():
    """Show tasks-focused main view"""
    st.title("📋 Tasks")
    
    # Get pending tasks
    pending_tasks = st.session_state.agent.get_filtered_items(ItemType.TASK, pending_only=True)
    completed_tasks = st.session_state.agent.get_filtered_items(ItemType.TASK, completed_only=True)
    all_tasks = st.session_state.agent.get_filtered_items(ItemType.TASK)
    
    # Show smart input
    show_smart_input()
    
    st.markdown("---")
    
    # Pending tasks
    if pending_tasks:
        st.subheader(f"🔄 Pending Tasks ({len(pending_tasks)})")
        
        for task in sorted(pending_tasks, key=lambda x: x.timestamp, reverse=True):
            with st.container():
                col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
                
                with col1:
                    st.write(f"**{task.enhanced_content}**")
                    st.caption(f"Created: {task.formatted_date}")
                
                with col2:
                    if st.button("✏️", key=f"edit_{task.id}", help="Edit task"):
                        st.session_state[f"editing_{task.id}"] = True
                        st.rerun()
                
                with col3:
                    if st.button("✅", key=f"complete_{task.id}", help="Complete task"):
                        result = st.session_state.agent.complete_task(task.id)
                        if result.success:
                            st.success("Task completed!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                with col4:
                    if st.button("🗑️", key=f"delete_{task.id}", help="Delete task"):
                        result = st.session_state.agent.delete_item(task.id)
                        if result.success:
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                # Edit dialog
                if st.session_state.get(f"editing_{task.id}", False):
                    with st.form(f"edit_form_{task.id}"):
                        st.write("**Edit Task:**")
                        
                        # Show original content
                        st.info(f"**Original:** {task.raw_content}")
                        st.caption(f"**Current Enhanced:** {task.enhanced_content}")
                        
                        new_content = st.text_area(
                            "New task content:",
                            value=task.raw_content,  # Use raw content as starting point
                            height=100,
                            help="Edit the original task content"
                        )
                        
                        col_save, col_cancel = st.columns(2)
                        with col_save:
                            if st.form_submit_button("💾 Save", use_container_width=True):
                                if new_content.strip() and new_content.strip() != task.raw_content:
                                    # Update the task content
                                    result = st.session_state.agent.update_item_content(task.id, new_content.strip())
                                    if result.success:
                                        st.success("Task updated!")
                                        st.session_state[f"editing_{task.id}"] = False
                                        st.rerun()
                                    else:
                                        st.error(result.message)
                                elif new_content.strip() == task.raw_content:
                                    st.info("No changes made.")
                                    st.session_state[f"editing_{task.id}"] = False
                                    st.rerun()
                        
                        with col_cancel:
                            if st.form_submit_button("❌ Cancel", use_container_width=True):
                                st.session_state[f"editing_{task.id}"] = False
                                st.rerun()
                
                st.divider()
    else:
        st.info("🎉 No pending tasks! You're all caught up.")
    
    # Completed tasks (collapsed by default)
    if completed_tasks:
        with st.expander(f"✅ Completed Tasks ({len(completed_tasks)})", expanded=False):
            for task in sorted(completed_tasks, key=lambda x: x.timestamp, reverse=True):
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.write(f"~~{task.enhanced_content}~~")
                    st.caption(f"Completed: {task.formatted_date}")
                with col2:
                    if st.button("🔄", key=f"reopen_{task.id}", help="Reopen task"):
                        result = st.session_state.agent.reopen_task(task.id)
                        if result.success:
                            st.success("Task reopened!")
                            st.rerun()
                        else:
                            st.error(result.message)
    else:
        st.info("ℹ️ No completed tasks yet.")

def show_notes_view():
    """Show notes view"""
    st.title("📝 Notes")
    
    show_smart_input()
    
    st.markdown("---")
    
    # Get all notes
    notes = st.session_state.agent.get_filtered_items(ItemType.NOTE)
    
    if notes:
        st.subheader(f"📝 All Notes ({len(notes)})")
        
        for note in sorted(notes, key=lambda x: x.timestamp, reverse=True):
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.write(f"**{note.enhanced_content}**")
                    st.caption(f"Created: {note.formatted_date}")
                
                with col2:
                    if st.button("🗑️", key=f"delete_note_{note.id}", help="Delete note"):
                        result = st.session_state.agent.delete_item(note.id)
                        if result.success:
                            st.success("Note deleted!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                st.divider()
    else:
        st.info("📝 No notes yet. Add your first note above!")

def show_resources_view():
    """Show resources view"""
    st.title("🔗 Resources")
    
    show_smart_input()
    
    st.markdown("---")
    
    # Get all resources
    resources = st.session_state.agent.get_filtered_items(ItemType.RESOURCE)
    
    if resources:
        st.subheader(f"🔗 All Resources ({len(resources)})")
        
        for resource in sorted(resources, key=lambda x: x.timestamp, reverse=True):
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.write(f"**{resource.enhanced_content}**")
                    st.caption(f"Added: {resource.formatted_date}")
                
                with col2:
                    if st.button("🗑️", key=f"delete_resource_{resource.id}", help="Delete resource"):
                        result = st.session_state.agent.delete_item(resource.id)
                        if result.success:
                            st.success("Resource deleted!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                st.divider()
    else:
        st.info("🔗 No resources yet. Add your first resource above!")

def show_search_view():
    """Show search view"""
    st.title("🔍 Search")
    
    # Search input
    search_query = st.text_input(
        "Search your notes, tasks, and resources:",
        placeholder="machine learning resources, pending tasks, meeting notes...",
        help="Search using natural language"
    )
    
    if search_query:
        with st.spinner("Searching..."):
            result = st.session_state.agent.search_items(search_query)
            
            if result.success and result.data:
                st.subheader(f"🔍 Search Results ({len(result.data)})")
                
                for search_result in result.data:
                    item = search_result.item
                    type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
                    
                    with st.container():
                        col1, col2, col3 = st.columns([4, 1, 1])
                        
                        with col1:
                            st.write(f"{type_emoji} **{item.enhanced_content}**")
                            st.caption(f"Type: {item.item_type.value.title()} | Created: {item.formatted_date}")
                            st.caption(f"Relevance: {search_result.similarity_score:.2f}")
                        
                        with col2:
                            if item.item_type == ItemType.TASK and not item.is_completed:
                                if st.button("✅", key=f"complete_search_{item.id}", help="Complete task"):
                                    result = st.session_state.agent.complete_task(item.id)
                                    if result.success:
                                        st.success("Task completed!")
                                        st.rerun()
                        
                        with col3:
                            if st.button("🗑️", key=f"delete_search_{item.id}", help="Delete item"):
                                result = st.session_state.agent.delete_item(item.id)
                                if result.success:
                                    st.success("Item deleted!")
                                    st.rerun()
                        
                        st.divider()
            else:
                st.info("No results found. Try different keywords.")

def show_all_items_view():
    """Show all items view"""
    st.title("📊 All Items")
    
    # Get all items
    all_items = st.session_state.agent.get_filtered_items()
    
    if all_items:
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by type:", ["All", "Tasks", "Notes", "Resources"])
        with col2:
            filter_status = st.selectbox("Filter by status:", ["All", "Pending", "Completed"])
        with col3:
            sort_by = st.selectbox("Sort by:", ["Newest", "Oldest", "Type"])
        
        # Apply filters
        filtered_items = all_items
        
        if filter_type != "All":
            type_map = {"Tasks": ItemType.TASK, "Notes": ItemType.NOTE, "Resources": ItemType.RESOURCE}
            filtered_items = [item for item in filtered_items if item.item_type == type_map[filter_type]]
        
        if filter_status != "All":
            if filter_status == "Pending":
                filtered_items = [item for item in filtered_items if not item.is_completed]
            else:  # Completed
                filtered_items = [item for item in filtered_items if item.is_completed]
        
        # Apply sorting
        if sort_by == "Newest":
            filtered_items = sorted(filtered_items, key=lambda x: x.timestamp, reverse=True)
        elif sort_by == "Oldest":
            filtered_items = sorted(filtered_items, key=lambda x: x.timestamp)
        else:  # Type
            filtered_items = sorted(filtered_items, key=lambda x: (x.item_type.value, x.timestamp), reverse=True)
        
        st.subheader(f"📊 Items ({len(filtered_items)})")
        
        for item in filtered_items:
            type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
            status_emoji = "✅" if item.is_completed else "🔄"
            
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    content = f"{status_emoji} {item.enhanced_content}" if item.is_completed else item.enhanced_content
                    st.write(f"{type_emoji} **{content}**")
                    st.caption(f"Type: {item.item_type.value.title()} | Created: {item.formatted_date}")
                
                with col2:
                    if item.item_type == ItemType.TASK and not item.is_completed:
                        if st.button("✅", key=f"complete_all_{item.id}", help="Complete task"):
                            result = st.session_state.agent.complete_task(item.id)
                            if result.success:
                                st.success("Task completed!")
                                st.rerun()
                
                with col3:
                    if st.button("🗑️", key=f"delete_all_{item.id}", help="Delete item"):
                        result = st.session_state.agent.delete_item(item.id)
                        if result.success:
                            st.success("Item deleted!")
                            st.rerun()
                
                st.divider()
    else:
        st.info("📊 No items yet. Add your first item!")

def show_backup_view():
    """Show backup and sync view"""
    st.title("☁️ Backup & Sync")
    
    # Import backup service
    from core.backup_service import BackupService
    backup_service = BackupService()
    
    # Google Drive sync section
    st.subheader("🔄 Google Drive Sync")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Sync to Google Drive", help="Backup and sync data to Google Drive", use_container_width=True):
            with st.spinner("Syncing to Google Drive..."):
                try:
                    # Check if Google Drive is set up
                    if not backup_service.metadata['google_drive_sync']['enabled']:
                        st.error("Google Drive not set up. Please set up Google Drive authentication first.")
                        st.info("To set up Google Drive:\n1. Download credentials from Google Cloud Console\n2. Place as 'google_drive_credentials.json' in app folder\n3. Run setup in terminal")
                    else:
                        success = backup_service.sync_to_google_drive()
                        if success:
                            st.success("✅ Data synced to Google Drive!")
                        else:
                            st.error("❌ Sync failed")
                except Exception as e:
                    st.error(f"Sync error: {str(e)}")
    
    with col2:
        if st.button("📊 Check Status", help="Check backup status", use_container_width=True):
            st.info("Checking backup status...")
            # Show status info
            if backup_service.metadata['google_drive_sync']['enabled']:
                last_sync = backup_service.metadata['google_drive_sync']['last_sync']
                if last_sync:
                    st.success(f"✅ Last sync: {last_sync[:10]}")
                else:
                    st.warning("⚠️ Never synced")
            else:
                st.error("❌ Google Drive not configured")
    
    # Show sync status
    if backup_service.metadata['google_drive_sync']['enabled']:
        last_sync = backup_service.metadata['google_drive_sync']['last_sync']
        if last_sync:
            st.success(f"✅ Last sync: {last_sync[:10]}")
        else:
            st.warning("⚠️ Never synced")
    else:
        st.error("❌ Google Drive not configured")
        st.info("Run: `python setup_google_drive.py` to set up Google Drive")
    
    st.markdown("---")
    
    # Local backup section
    st.subheader("💾 Local Backup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📦 Create Backup", help="Create local backup", use_container_width=True):
            with st.spinner("Creating backup..."):
                try:
                    backup_path = backup_service.create_compressed_backup()
                    st.success(f"✅ Backup created: {backup_path}")
                except Exception as e:
                    st.error(f"Backup failed: {str(e)}")
    
    with col2:
        if st.button("📋 List Backups", help="Show available backups", use_container_width=True):
            try:
                backups = backup_service.list_backups()
                if backups:
                    st.subheader(f"📋 Available Backups ({len(backups)})")
                    for backup in backups[:5]:  # Show first 5
                        st.write(f"• {backup['backup_name']} ({backup['timestamp']})")
                else:
                    st.info("No backups found")
            except Exception as e:
                st.error(f"Error listing backups: {str(e)}")

def show_stats_sidebar():
    """Show minimal statistics in sidebar"""
    with st.sidebar:
        st.header("📊 Quick Stats")
        
        stats = st.session_state.agent.get_stats()
        
        # Show only essential stats
        pending_tasks = stats.get('pending_tasks', 0)
        total_items = stats.get('total_items', 0)
        
        st.metric("Open Tasks", pending_tasks)
        st.metric("Total Items", total_items)
        
        # AI Provider status
        st.divider()
        current_provider = st.session_state.agent.ai_service.get_current_provider()
        provider_status = "🟢 Connected" if st.session_state.agent.ai_service.is_configured() else "🔴 Not configured"
        st.write(f"**AI Provider:** {current_provider.title()}")
        st.write(f"**Status:** {provider_status}")
        
        if st.button("⚙️ Settings", key="sidebar_settings"):
            # Set flag to show settings page
            st.session_state.show_settings = True
            st.rerun()

def show_main_app():
    """Show the main app with new UX"""
    # Header
    st.title("🧠 AI Notes")
    st.caption("Smart note-taking and task management powered by AI")
    
    # Show navigation
    show_navigation()
    
    # Show sidebar stats
    show_stats_sidebar()
    
    # Show current view
    if st.session_state.current_view == "tasks":
        show_tasks_view()
    elif st.session_state.current_view == "notes":
        show_notes_view()
    elif st.session_state.current_view == "resources":
        show_resources_view()
    elif st.session_state.current_view == "search":
        show_search_view()
    elif st.session_state.current_view == "all":
        show_all_items_view()
    elif st.session_state.current_view == "backup":
        show_backup_view()

def main():
    """Main application entry point"""
    init_session_state()
    
    # Check if app is initialized
    if not st.session_state.initialized:
        show_setup_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
