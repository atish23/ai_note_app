#!/usr/bin/env python3
"""
Native macOS App Wrapper for AI Notes/Task Manager
Embeds the Streamlit app in a native macOS window
"""
import sys
import os
import subprocess
import threading
import time
import signal
from pathlib import Path

# PyQt6 imports for native macOS app
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QMenuBar, QMenu, QMessageBox, QSystemTrayIcon,
    QStyle, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QTimer, pyqtSignal, QThread, Qt

class StreamlitServer(QThread):
    """Thread to manage Streamlit server"""
    server_ready = pyqtSignal(str)
    server_error = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.process = None
        self.server_url = None
        
    def run(self):
        """Start Streamlit server"""
        try:
            # Get the app directory
            app_dir = Path(__file__).parent
            streamlit_script = app_dir / "ai_note_app.py"
            
            # Start Streamlit server
            self.process = subprocess.Popen(
                [
                    sys.executable, "-m", "streamlit", "run",
                    str(streamlit_script),
                    "--server.headless", "true",
                    "--server.port", "8501",
                    "--server.address", "localhost"
                ],
                cwd=app_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(3)
            self.server_url = "http://localhost:8501"
            self.server_ready.emit(self.server_url)
            
            # Keep the process running
            self.process.wait()
            
        except Exception as e:
            self.server_error.emit(str(e))
    
    def stop(self):
        """Stop Streamlit server"""
        if self.process:
            self.process.terminate()
            self.process.wait()

class AINotesMacApp(QMainWindow):
    """Native macOS app window"""
    
    def __init__(self):
        super().__init__()
        self.streamlit_server = None
        self.web_view = None
        self.tray_icon = None
        self.init_ui()
        self.start_streamlit_server()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("🧠 AI Notes/Task Manager")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set app icon (you can add an icon file later)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Create loading indicator
        self.loading_label = QLabel("Starting AI Notes App...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #666;
                padding: 20px;
            }
        """)
        layout.addWidget(self.loading_label)
        
        # Create WebView for Streamlit app
        self.web_view = QWebEngineView()
        self.web_view.setMinimumSize(800, 600)
        layout.addWidget(self.web_view)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create system tray icon
        self.create_system_tray()
        
        # Set window properties for macOS
        self.setUnifiedTitleAndToolBarOnMac(True)
        
    def create_menu_bar(self):
        """Create native macOS menu bar"""
        menubar = self.menuBar()
        
        # App menu
        app_menu = menubar.addMenu("AI Notes")
        
        # About action
        about_action = QAction("About AI Notes", self)
        about_action.triggered.connect(self.show_about)
        app_menu.addAction(about_action)
        
        app_menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Cmd+Q")
        quit_action.triggered.connect(self.close)
        app_menu.addAction(quit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Refresh action
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut("Cmd+R")
        refresh_action.triggered.connect(self.refresh_app)
        view_menu.addAction(refresh_action)
        
        # Window menu
        window_menu = menubar.addMenu("Window")
        
        # Minimize action
        minimize_action = QAction("Minimize", self)
        minimize_action.setShortcut("Cmd+M")
        minimize_action.triggered.connect(self.showMinimized)
        window_menu.addAction(minimize_action)
        
    def create_system_tray(self):
        """Create system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def start_streamlit_server(self):
        """Start the Streamlit server in background"""
        self.streamlit_server = StreamlitServer()
        self.streamlit_server.server_ready.connect(self.on_server_ready)
        self.streamlit_server.server_error.connect(self.on_server_error)
        self.streamlit_server.start()
        
    def on_server_ready(self, url):
        """Called when Streamlit server is ready"""
        self.loading_label.setText("Loading AI Notes App...")
        
        # Load the Streamlit app in WebView
        self.web_view.setUrl(QUrl(url))
        
        # Hide loading indicator after a short delay
        QTimer.singleShot(2000, lambda: self.loading_label.hide())
        
    def on_server_error(self, error):
        """Called when Streamlit server fails to start"""
        QMessageBox.critical(
            self,
            "Server Error",
            f"Failed to start Streamlit server:\n{error}"
        )
        
    def refresh_app(self):
        """Refresh the app"""
        if self.web_view:
            self.web_view.reload()
            
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About AI Notes",
            """
            <h3>🧠 AI Notes/Task Manager</h3>
            <p>An intelligent note-taking and task management system powered by AI.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>Smart item creation with AI enhancement</li>
                <li>Semantic search capabilities</li>
                <li>Multi-LLM support (Gemini/Ollama)</li>
                <li>Task management and completion tracking</li>
            </ul>
            """
        )
        
    def closeEvent(self, event):
        """Handle app close event"""
        # Stop Streamlit server
        if self.streamlit_server:
            self.streamlit_server.stop()
            
        # Hide system tray icon
        if self.tray_icon:
            self.tray_icon.hide()
            
        event.accept()
        
    def changeEvent(self, event):
        """Handle window state changes"""
        if event.type() == event.Type.WindowStateChange:
            if self.isMinimized():
                # Hide to system tray when minimized
                self.hide()
                event.ignore()
            else:
                event.accept()

def main():
    """Main application entry point"""
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("AI Notes")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AI Notes")
    
    # Create and show main window
    window = AINotesMacApp()
    window.show()
    
    # Run the application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
