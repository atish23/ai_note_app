"""
AI Notes/Task Manager - Full Featured (No AI Chat)
"""
import streamlit as st
import time
from typing import Optional

# Import shared agent service
from core.agent_service import NotesAgentService
from core.models import ItemType

# ---------- CONFIG ----------------------------------------------------------
st.set_page_config(
    page_title="AI Notes/Task Manager",
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
        
    if 'selected_filter' not in st.session_state:
        st.session_state.selected_filter = "All"

# ---------- UI FUNCTIONS ----------------------------------------------------

def show_setup_page():
    """Show API key setup page"""
    st.title("🧠 AI Notes/Task Manager")
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
            st.info("Please configure your Gemini API key to continue.")
            with st.form("api_key_form"):
                api_key_input = st.text_input(
                    "Enter your Gemini API Key:",
                    type="password",
                    help="Get your API key from https://makersuite.google.com/app/apikey"
                )
                
                submit = st.form_submit_button("Save & Continue")
                
                if submit and api_key_input:
                    # Save API key
                    st.session_state.agent.ai_service.save_api_key(api_key_input)
                    
                    # Initialize agent
                    if st.session_state.agent.initialize():
                        st.session_state.initialized = True
                        st.rerun()
                    else:
                        st.error("Invalid API key or initialization failed.")
    
    elif current_provider == "ollama":
        st.info("**Ollama Setup Instructions:**")
        st.markdown("""
        1. Install Ollama from https://ollama.ai
        2. Run: `ollama pull llama3.2:3b` (for text generation)
        3. Run: `ollama pull nomic-embed-text` (for embeddings)
        4. Make sure Ollama is running (`ollama serve`)
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Test Ollama Connection"):
                with st.spinner("Testing Ollama connection..."):
                    if st.session_state.agent.initialize():
                        st.success("✅ Ollama connected successfully!")
                        st.session_state.initialized = True
                        st.rerun()
                    else:
                        st.error("❌ Could not connect to Ollama. Make sure it's running on localhost:11434")
                        st.info("Run `ollama serve` in your terminal first.")
        
        with col2:
            if st.button("Auto-Setup Ollama"):
                st.info("Run this command in your terminal:")
                st.code("./run.sh setup-ollama")
                st.write("Then come back and click 'Test Ollama Connection'")
    
    # Help section
    with st.expander("💡 Need Help?"):
        st.markdown("""
        **Gemini (Recommended for most users):**
        - Fast and high-quality responses
        - Requires Google AI API key (free tier available)
        - Get API key: https://makersuite.google.com/app/apikey
        
        **Ollama (For privacy/offline use):**
        - Runs completely on your machine
        - No external API calls
        - Requires more setup and system resources
        - Install guide: https://ollama.ai
        
        **Switching Providers:**
        You can switch between providers anytime from this setup page.
        """)

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
        
        # Quick actions
        st.divider()
        st.subheader("⚡ Quick Actions")
        
        if st.button("🔍 Search All", key="sidebar_search"):
            st.session_state.current_tab = "search"
            st.rerun()
            
        if st.button("📋 Browse All", key="sidebar_browse"):
            st.session_state.current_tab = "browse"
            st.rerun()

def show_main_dashboard():
    """Show clean main dashboard with tasks and quick add"""
    st.title("🧠 Pending Tasks")

    # Sidebar
    show_stats_sidebar()
    
    # Main content - two column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_open_tasks()
    
    with col2:
        show_quick_add_panel()

def show_open_tasks():
    """Show open/pending tasks in a clean format"""
    st.subheader("📋 Open Tasks")
    
    # Get pending tasks
    pending_tasks = st.session_state.agent.get_filtered_items(ItemType.TASK, pending_only=True)
    
    if pending_tasks:
        # Sort by newest first
        pending_tasks = sorted(pending_tasks, key=lambda x: x.timestamp, reverse=True)
        
        for task in pending_tasks:
            with st.container():
                col1, col2, col3 = st.columns([4, 1, 1])
                
                with col1:
                    st.write(f"**#{task.id}** {task.enhanced_content}")
                    st.caption(f"Created: {task.formatted_date}")
                
                with col2:
                    if st.button("✅", key=f"complete_{task.id}", help="Complete task"):
                        result = st.session_state.agent.complete_task(task.id)
                        if result.success:
                            st.success("Task completed!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                with col3:
                    if st.button("🗑️", key=f"delete_{task.id}", help="Delete task"):
                        result = st.session_state.agent.delete_item(task.id)
                        if result.success:
                            st.success("Task deleted!")
                            st.rerun()
                        else:
                            st.error(result.message)
                
                st.divider()
    else:
        st.info("🎉 No open tasks! You're all caught up.")
        st.write("Add a new task using the panel on the right →")

def show_quick_add_panel():
    """Show quick add panel - NO AI CHAT"""
    st.subheader("➕ Quick Add")
    
    # Only show Quick Add mode (removed AI Chat)
    with st.form("quick_add", clear_on_submit=True):
        content = st.text_area(
            "What's on your mind?",
            placeholder="Type anything...\n\n• Start with @task for tasks\n• Start with @note for notes\n• Include links for resources",
            height=120
        )
        
        submitted = st.form_submit_button("Add", type="primary", use_container_width=True)
        
        if submitted and content.strip():
            with st.spinner("Adding..."):
                result = st.session_state.agent.create_item(content.strip())
                
                if result.success:
                    item = result.data
                    type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(getattr(item, 'item_type', None) and item.item_type.value, "📝")
                    # Show enhanced content if available
                    enhanced = getattr(item, 'enhanced_content', None)
                    msg = f"{type_emoji} Added {item.item_type.value}!"
                    if enhanced:
                        msg += f"\n{enhanced}"
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(f"Error: {result.message}")
    
    # Quick tips
    with st.expander("💡 Quick Tips"):
        st.markdown("""
        **Smart Detection:**
        - Words like "need to", "must", "deadline" → Task
        - URLs or "documentation" → Resource  
        - Everything else → Note
        
        **Force Type:**
        - `@task Fix the login bug`
        - `@note Meeting insights`
        - `@resource https://docs.example.com`
        """)

def show_search_page():
    """Dedicated search page"""
    st.title("🔍 Search Everything")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_tab = "dashboard"
        st.rerun()
    
    st.divider()
    
    # Search input
    search_query = st.text_input(
        "Search your content:",
        placeholder="e.g., machine learning, meeting notes, productivity tools...",
        key="search_input"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        max_results = st.number_input("Max Results", 1, 20, 10)
    
    if st.button("🔍 Search", type="primary") and search_query:
        with st.spinner("Searching..."):
            result = st.session_state.agent.search_items(search_query, max_results, 0.6)
            
            if result.success and result.data:
                st.success(f"Found {len(result.data)} results")
                
                for search_result in result.data:
                    item = search_result.item
                    score = search_result.similarity_score
                    
                    type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
                    status_text = " (Completed)" if item.is_completed else ""
                    
                    with st.expander(f"{type_emoji} #{item.id} - {item.enhanced_content[:50]}...{status_text}"):
                        st.write(f"**Content:** {item.enhanced_content}")
                        st.write(f"**Created:** {item.formatted_date}")
                        st.write(f"**Similarity:** {score:.2f}")
                        
                        # Quick actions
                        col1, col2, col3 = st.columns(3)
                        
                        if item.item_type == ItemType.TASK and not item.is_completed:
                            with col1:
                                if st.button("✅ Complete", key=f"search_complete_{item.id}"):
                                    st.session_state.agent.complete_task(item.id)
                                    st.rerun()
                        
                        with col2:
                            if st.button("🗑️ Delete", key=f"search_delete_{item.id}"):
                                st.session_state.agent.delete_item(item.id)
                                st.rerun()
            else:
                st.info("No results found. Try different keywords.")

def show_browse_page():
    """Dedicated browse page"""
    st.title("📋 Browse All Items")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.current_tab = "dashboard"
        st.rerun()
    
    st.divider()
    
    # Simple filters
    col1, col2 = st.columns(2)
    
    with col1:
        type_filter = st.selectbox("Filter by Type:", ["All", "Tasks", "Notes", "Resources"])
    
    with col2:
        status_filter = st.selectbox("Status:", ["All", "Active", "Completed"])
    
    # Get items
    item_type = None
    if type_filter == "Tasks":
        item_type = ItemType.TASK
    elif type_filter == "Notes":
        item_type = ItemType.NOTE
    elif type_filter == "Resources":
        item_type = ItemType.RESOURCE
    
    if status_filter == "Active":
        items = st.session_state.agent.get_filtered_items(item_type, pending_only=True)
    elif status_filter == "Completed":
        items = st.session_state.agent.get_filtered_items(item_type, completed_only=True)
    else:
        items = st.session_state.agent.get_filtered_items(item_type)
    
    # Sort by newest first
    items = sorted(items, key=lambda x: x.timestamp, reverse=True)
    
    if items:
        st.info(f"Showing {len(items)} items")
        
        for item in items:
            type_emoji = {"note": "📝", "task": "✅", "resource": "🔗"}.get(item.item_type.value, "📝")
            status_text = " (Completed)" if item.is_completed else ""
            
            with st.expander(f"{type_emoji} #{item.id} - {item.enhanced_content[:60]}...{status_text}"):
                st.write(f"**Content:** {item.enhanced_content}")
                st.write(f"**Original:** {item.raw_content}")
                st.write(f"**Created:** {item.formatted_date}")
                
                # Actions
                col1, col2, col3 = st.columns(3)
                
                if item.item_type == ItemType.TASK:
                    with col1:
                        if item.is_completed:
                            if st.button("↩️ Reopen", key=f"browse_reopen_{item.id}"):
                                st.session_state.agent.reopen_task(item.id)
                                st.rerun()
                        else:
                            if st.button("✅ Complete", key=f"browse_complete_{item.id}"):
                                st.session_state.agent.complete_task(item.id)
                                st.rerun()
                
                with col2:
                    if st.button("🗑️ Delete", key=f"browse_delete_{item.id}"):
                        st.session_state.agent.delete_item(item.id)
                        st.rerun()
    else:
        st.info("No items found with current filters.")

def show_main_app():
    """Show main application with clean navigation"""
    # Initialize current tab in session state
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "dashboard"
    
    # Show appropriate page based on current tab
    if st.session_state.current_tab == "search":
        show_search_page()
    elif st.session_state.current_tab == "browse":
        show_browse_page()
    else:
        show_main_dashboard()

# ---------- MAIN APP --------------------------------------------------------

def main():
    """Main application entry point"""
    init_session_state()
    
    # Check if user wants to go to settings
    if 'show_settings' in st.session_state and st.session_state.show_settings:
        st.session_state.show_settings = False  # Reset flag
        show_setup_page()
        return
    
    # Only show setup automatically if key is missing or initialization fails
    api_key = st.session_state.agent.ai_service.get_api_key()
    current_provider = st.session_state.agent.ai_service.get_current_provider()
    
    # For Gemini, check API key. For Ollama, check if configured
    needs_setup = False
    if current_provider == "gemini" and not api_key:
        needs_setup = True
    elif not st.session_state.agent.ai_service.is_configured():
        needs_setup = True
    
    if needs_setup:
        show_setup_page()
        return
        
    # Try to initialize if not already
    if not st.session_state.initialized:
        if st.session_state.agent.initialize():
            st.session_state.initialized = True
            show_main_app()
        else:
            show_setup_page()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
