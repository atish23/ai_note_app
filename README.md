# 🧠 AI Notes/Task Manager

An intelligent note-taking and task management system powered by AI with multi-LLM support.

## ✨ Features

- **Smart Item Creation**: Automatically detects notes, tasks, and resources
- **AI Enhancement**: Improves your content using AI
- **Semantic Search**: Find items using natural language
- **Multi-LLM Support**: Works with Gemini (cloud) or Ollama (local)
- **Tag System**: Use `@task`, `@note`, `@resource` to force types

## 🚀 Quick Start

### 1. Setup
```bash
./run.sh setup
```

### 2. Choose AI Provider
- **Gemini (Recommended)**: Get API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Ollama (Local)**: Install from [ollama.ai](https://ollama.ai) then run `./run.sh setup-ollama`

### 3. Run App
```bash
./run.sh streamlit
```

## 💡 Usage

### Smart Item Creation
```
I need to finish the report by Friday
@task Fix the login bug
@note Meeting insights from today
@resource https://docs.example.com
```

### Search & Manage
- Search: "machine learning resources" or "pending tasks"
- Complete tasks with ✅ button
- Browse and filter by type/status

## 📁 Project Structure

```
AI_Note_App/
├── ai_note_app.py          # Main Streamlit app
├── mcp_server.py          # MCP server (optional)
├── run.sh                 # Management script
├── requirements.txt       # Dependencies
└── core/
    ├── agent_service.py   # Main business logic
    ├── ai_service.py      # AI provider abstraction
    ├── database_service.py # Data persistence
    ├── search_service.py  # Semantic search
    └── models.py          # Data models
```

## 🛠 Commands

```bash
./run.sh setup         # Install dependencies
./run.sh setup-ollama  # Setup local AI
./run.sh streamlit     # Run web app
./run.sh help          # Show help
```

## 🔧 Configuration

The app automatically creates `llm_config.json` with your provider settings. You can switch between Gemini and Ollama anytime in the setup page.

## 📋 Requirements

- Python 3.8+
- For Gemini: API key from Google AI Studio
- For Ollama: Local Ollama installation

That's it! Simple, powerful, and AI-enhanced note management.