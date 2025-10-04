import sys
import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from browser.browser_window import BrowserWindow

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Clean up any old browser data
    if os.path.exists("./web_data"):
        import shutil
        shutil.rmtree("./web_data")
    if os.path.exists("./web_cache"):
        import shutil
        shutil.rmtree("./web_cache")
    
    # Enhanced flags for better compatibility
    chrome_flags = [
        '--ignore-certificate-errors',
        '--ignore-ssl-errors',
        '--no-sandbox',
        '--disable-web-security',
        '--allow-running-insecure-content',
        '--disable-features=BlockInsecurePrivateNetworkRequests',
        '--enable-features=NetworkServiceInProcess',
        '--disable-site-isolation-trials',
        '--disable-background-timer-throttling',
        '--disable-renderer-backgrounding'
    ]
    
    os.environ['QTWEBENGINE_CHROMIUM_FLAGS'] = ' '.join(chrome_flags)
    os.environ['QTWEBENGINE_DISABLE_SANDBOX'] = '1'
    
    app = QApplication(sys.argv)
    app.setApplicationName("LightPy Browser")
    app.setApplicationVersion("1.0.0")
    
    # Set style
    app.setStyle('Fusion')
    
    # Apply dark theme
    apply_dark_theme(app)
    
    # Create and show main window
    window = BrowserWindow()
    window.show()
    
    sys.exit(app.exec_())

def apply_dark_theme(app):
    """Apply a dark theme to the application"""
    dark_stylesheet = """
    QMainWindow {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #ffffff;
    }
    QTabWidget::pane {
        border: 1px solid #555;
        background-color: #2b2b2b;
    }
    QTabBar::tab {
        background-color: #3b3b3b;
        color: #ffffff;
        padding: 8px 12px;
        margin-right: 2px;
    }
    QTabBar::tab:selected {
        background-color: #505050;
    }
    QLineEdit {
        background-color: #3b3b3b;
        color: #ffffff;
        border: 1px solid #555;
        padding: 5px;
        border-radius: 3px;
    }
    QToolButton {
        background-color: #3b3b3b;
        color: #ffffff;
        border: 1px solid #555;
        padding: 5px;
        border-radius: 3px;
        min-width: 30px;
    }
    QToolButton:hover {
        background-color: #505050;
    }
    QProgressBar {
        border: none;
        background-color: #3b3b3b;
        height: 3px;
    }
    QProgressBar::chunk {
        background-color: #4CAF50;
    }
    QStatusBar {
        background-color: #3b3b3b;
        color: #ffffff;
    }
    """
    app.setStyleSheet(dark_stylesheet)

if __name__ == "__main__":
    main()
