from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import QWebEngineSettings
from .tab_manager import TabManager
from .navigation_bar import NavigationBar
from .bookmark_manager import BookmarkManager
import json
import os

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LightPy Browser")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize managers
        self.bookmark_manager = BookmarkManager()
        self.settings = self.load_settings()
        
        self.setup_ui()
        self.setup_shortcuts()
        
    def setup_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create navigation bar
        self.nav_bar = NavigationBar()
        self.nav_bar.url_bar.returnPressed.connect(self.navigate_to_url)
        self.nav_bar.back_btn.clicked.connect(self.go_back)
        self.nav_bar.forward_btn.clicked.connect(self.go_forward)
        self.nav_bar.reload_btn.clicked.connect(self.reload_page)
        self.nav_bar.home_btn.clicked.connect(self.go_home)
        self.nav_bar.bookmark_btn.clicked.connect(self.toggle_bookmark)
        
        layout.addWidget(self.nav_bar)
        
        # Create bookmarks bar
        self.bookmarks_bar = QToolBar("Bookmarks")
        self.bookmarks_bar.setIconSize(QSize(16, 16))
        self.bookmarks_bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.bookmarks_bar.setVisible(True)  # Can be toggled in settings later
        layout.addWidget(self.bookmarks_bar)
        
        # Load bookmarks into bookmarks bar
        self.refresh_bookmarks_bar()
        
        # Create tab widget
        self.tab_manager = TabManager()
        self.tab_manager.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(self.tab_manager)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add first tab
        self.add_new_tab("https://duckduckgo.com/", "Home")
        
    def refresh_bookmarks_bar(self):
        """Refresh the bookmarks bar with current bookmarks"""
        # Clear existing bookmarks
        self.bookmarks_bar.clear()
        
        # Add bookmarks to the bar
        bookmarks = self.bookmark_manager.get_bookmarks()
        for bookmark in bookmarks:
            action = QAction(bookmark['title'], self)
            action.setToolTip(bookmark['url'])
            action.triggered.connect(lambda checked=False, url=bookmark['url']: self.open_bookmark(url))
            self.bookmarks_bar.addAction(action)
        
    def open_bookmark(self, url):
        """Open a bookmark in the current tab"""
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(url))
        
    def setup_shortcuts(self):
        # Keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, self.add_new_tab)
        QShortcut(QKeySequence("Ctrl+W"), self, self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+R"), self, self.reload_page)
        QShortcut(QKeySequence("Ctrl+L"), self, self.focus_url_bar)
        QShortcut(QKeySequence("Ctrl++"), self, self.zoom_in)
        QShortcut(QKeySequence("Ctrl+-"), self, self.zoom_out)
        QShortcut(QKeySequence("Ctrl+0"), self, self.zoom_reset)
        QShortcut(QKeySequence("Ctrl+H"), self, self.show_history)
        QShortcut(QKeySequence("Ctrl+B"), self, self.show_bookmarks)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+click"), self, self.open_link_in_new_tab)
        
    def create_browser(self):
        """Create a browser instance with SSL error handling"""
        browser = QWebEngineView()
        
        # Configure browser settings for better compatibility
        settings = browser.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        settings.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)
        
        return browser
        
    def add_new_tab(self, url=None, title="New Tab"):
        """Add a new browser tab"""
        if url is None:
            url = self.settings.get('home_page', 'https://duckduckgo.com/')
            
        browser = self.create_browser()
        browser.setUrl(QUrl(url))
        
        # Connect signals
        browser.urlChanged.connect(lambda url: self.on_url_changed(browser, url))
        browser.titleChanged.connect(lambda title: self.on_title_changed(browser, title))
        browser.loadProgress.connect(lambda progress: self.on_load_progress(progress))
        browser.loadStarted.connect(self.on_load_started)
        browser.loadFinished.connect(self.on_load_finished)
        
        # Context menu for browser
        browser.setContextMenuPolicy(Qt.CustomContextMenu)
        browser.customContextMenuRequested.connect(
            lambda pos: self.show_context_menu(browser, pos)
        )
        
        tab_index = self.tab_manager.add_tab(browser, title)
        self.tab_manager.setCurrentIndex(tab_index)
        
        # Focus URL bar when new tab is created
        QTimer.singleShot(100, self.focus_url_bar)
        
        return browser
        
    def close_current_tab(self):
        """Close the current tab"""
        if self.tab_manager.count() > 1:
            self.tab_manager.close_current_tab()
        else:
            self.close()
            
    def navigate_to_url(self):
        """Navigate to URL from address bar"""
        url = self.nav_bar.url_bar.text().strip()
        if not url:
            return
            
        # Check if it's a search query
        if not any(url.startswith(prefix) for prefix in ['http://', 'https://', 'file://', 'ftp://']):
            if '.' in url and ' ' not in url:
                url = 'https://' + url
            else:
                search_engine = self.settings.get('search_engine', 'https://duckduckgo.com/search?q=')
                url = search_engine + url.replace(' ', '+')
        
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(url))
            
    def go_back(self):
        """Navigate back"""
        current_browser = self.get_current_browser()
        if current_browser and current_browser.history().canGoBack():
            current_browser.back()
            
    def go_forward(self):
        """Navigate forward"""
        current_browser = self.get_current_browser()
        if current_browser and current_browser.history().canGoForward():
            current_browser.forward()
            
    def reload_page(self):
        """Reload current page"""
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.reload()
            
    def go_home(self):
        """Go to home page"""
        home_url = self.settings.get('home_page', 'https://duckduckgo.com/')
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setUrl(QUrl(home_url))
            
    def toggle_bookmark(self):
        """Toggle bookmark for current page"""
        current_browser = self.get_current_browser()
        if current_browser:
            url = current_browser.url().toString()
            title = current_browser.title()
            is_bookmarked = self.bookmark_manager.toggle_bookmark(url, title)
            
            # Update bookmark button appearance
            if is_bookmarked:
                self.nav_bar.bookmark_btn.setText('★')
                self.nav_bar.bookmark_btn.setToolTip('Remove bookmark')
                self.status_bar.showMessage(f"Bookmarked: {title}", 3000)
            else:
                self.nav_bar.bookmark_btn.setText('☆')
                self.nav_bar.bookmark_btn.setToolTip('Bookmark this page')
                self.status_bar.showMessage("Bookmark removed", 3000)
            
            # Refresh bookmarks bar
            self.refresh_bookmarks_bar()
            
    def focus_url_bar(self):
        """Focus the URL bar"""
        self.nav_bar.url_bar.selectAll()
        self.nav_bar.url_bar.setFocus()
        
    def zoom_in(self):
        """Zoom in current page"""
        current_browser = self.get_current_browser()
        if current_browser:
            current_zoom = current_browser.zoomFactor()
            new_zoom = min(current_zoom + 0.1, 3.0)  # Max zoom 300%
            current_browser.setZoomFactor(new_zoom)
            self.status_bar.showMessage(f"Zoom: {int(new_zoom * 100)}%", 2000)
            
    def zoom_out(self):
        """Zoom out current page"""
        current_browser = self.get_current_browser()
        if current_browser:
            current_zoom = current_browser.zoomFactor()
            new_zoom = max(current_zoom - 0.1, 0.25)  # Min zoom 25%
            current_browser.setZoomFactor(new_zoom)
            self.status_bar.showMessage(f"Zoom: {int(new_zoom * 100)}%", 2000)
            
    def zoom_reset(self):
        """Reset zoom level"""
        current_browser = self.get_current_browser()
        if current_browser:
            current_browser.setZoomFactor(1.0)
            self.status_bar.showMessage("Zoom reset to 100%", 2000)
            
    def show_history(self):
        """Show browsing history (placeholder)"""
        self.status_bar.showMessage("History feature coming soon...", 3000)
        
    def show_bookmarks(self):
        """Show bookmarks manager"""
        bookmarks = self.bookmark_manager.get_bookmarks()
        if bookmarks:
            msg = "Bookmarks:\n" + "\n".join([f"• {b['title']}" for b in bookmarks[:5]])
            if len(bookmarks) > 5:
                msg += f"\n... and {len(bookmarks) - 5} more"
        else:
            msg = "No bookmarks yet"
            
        QMessageBox.information(self, "Bookmarks", msg)
            
    def get_current_browser(self):
        """Get current browser widget"""
        return self.tab_manager.currentWidget()
        
    def show_context_menu(self, browser, position):
        """Show right-click context menu"""
        menu = QMenu(self)
        
        # Get link under cursor if any
        page = browser.page()
        context_data = page.contextMenuData()
        link_url = context_data.linkUrl().toString() if not context_data.linkUrl().isEmpty() else None
        
        # Basic actions
        back_action = menu.addAction("Back")
        forward_action = menu.addAction("Forward")
        reload_action = menu.addAction("Reload")
        menu.addSeparator()
        
        # Link-specific actions
        if link_url:
            open_link_action = menu.addAction("Open Link")
            open_link_new_tab_action = menu.addAction("Open Link in New Tab")
            save_link_action = menu.addAction("Save Link As...")
            menu.addSeparator()
            
        # Page actions
        view_source_action = menu.addAction("View Page Source")
        inspect_action = menu.addAction("Inspect Element")
        menu.addSeparator()
        
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        
        # Connect actions
        back_action.triggered.connect(browser.back)
        forward_action.triggered.connect(browser.forward)
        reload_action.triggered.connect(browser.reload)
        
        if link_url:
            open_link_action.triggered.connect(lambda: browser.setUrl(QUrl(link_url)))
            open_link_new_tab_action.triggered.connect(lambda: self.add_new_tab(link_url))
            save_link_action.triggered.connect(lambda: self.save_link_as(link_url))
            
        view_source_action.triggered.connect(lambda: self.view_page_source(browser))
        inspect_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.InspectElement))
        copy_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.Copy))
        paste_action.triggered.connect(lambda: browser.page().triggerAction(QWebEnginePage.Paste))
        
        menu.exec_(browser.mapToGlobal(position))
        
    def save_link_as(self, link_url):
        """Save link target to downloads directory"""
        try:
            # Extract filename from URL or use a default name
            filename = os.path.basename(link_url)
            if not filename or '.' not in filename:
                filename = "downloaded_file"
                
            # Get downloads directory
            downloads_dir = self.settings.get('download_path', os.path.expanduser('~/Downloads'))
            os.makedirs(downloads_dir, exist_ok=True)
            
            # Create file path
            file_path = os.path.join(downloads_dir, filename)
            
            # Download the file
            current_browser = self.get_current_browser()
            if current_browser:
                current_browser.page().profile().downloadRequested.connect(
                    lambda download: download.setPath(file_path)
                )
                
            # Start download
            current_browser.page().profile().download(link_url)
            self.status_bar.showMessage(f"Downloading: {filename}", 3000)
            
        except Exception as e:
            QMessageBox.warning(self, "Download Error", f"Failed to download file: {str(e)}")
        
    def view_page_source(self, browser):
        """View page source in new tab"""
        def handle_source(content):
            source_browser = self.add_new_tab(None, "Page Source")
            source_browser.setHtml(f"<pre>{content}</pre>")
            
        browser.page().toPlainText(handle_source)
        
    def open_link_in_new_tab(self):
        """Handle Ctrl+click to open links in new tabs"""
        # This is handled by the browser's default behavior when Ctrl is pressed
        # The actual implementation would require intercepting navigation events
        pass
        
    # Signal handlers
    def on_url_changed(self, browser, url):
        if browser == self.get_current_browser():
            self.nav_bar.url_bar.setText(url.toString())
            
            # Update bookmark button state
            current_url = url.toString()
            is_bookmarked = any(b['url'] == current_url for b in self.bookmark_manager.get_bookmarks())
            self.nav_bar.bookmark_btn.setText('★' if is_bookmarked else '☆')
            self.nav_bar.bookmark_btn.setToolTip(
                'Remove bookmark' if is_bookmarked else 'Bookmark this page'
            )
            
    def on_title_changed(self, browser, title):
        self.tab_manager.set_tab_title(browser, title)
        if browser == self.get_current_browser():
            self.setWindowTitle(f"{title} - LightPy Browser")
            
    def on_tab_changed(self, index):
        browser = self.tab_manager.widget(index)
        if browser:
            current_url = browser.url().toString()
            self.nav_bar.url_bar.setText(current_url)
            
            # Update bookmark button for current page
            is_bookmarked = any(b['url'] == current_url for b in self.bookmark_manager.get_bookmarks())
            self.nav_bar.bookmark_btn.setText('★' if is_bookmarked else '☆')
            self.nav_bar.bookmark_btn.setToolTip(
                'Remove bookmark' if is_bookmarked else 'Bookmark this page'
            )
            
    def on_load_progress(self, progress):
        self.nav_bar.update_load_progress(progress)
        
    def on_load_started(self):
        self.status_bar.showMessage("Loading...")
        
    def on_load_finished(self, success):
        if success:
            self.status_bar.showMessage("Ready")
        else:
            self.status_bar.showMessage("Failed to load page")
        self.nav_bar.update_load_progress(0)
        
    def load_settings(self):
        """Load browser settings"""
        settings_file = "browser_settings.json"
        default_settings = {
            'home_page': 'https://duckduckgo.com/',
            'search_engine': 'https://duckduckgo.com/search?q=',
            'download_path': os.path.expanduser('~/Downloads'),
            'default_zoom': 1.0
        }
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    return {**default_settings, **loaded_settings}
        except Exception as e:
            print(f"Error loading settings: {e}")
            
        return default_settings
        
    def save_settings(self):
        """Save browser settings"""
        settings_file = "browser_settings.json"
        try:
            with open(settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
        
    def closeEvent(self, event):
        """Save settings when closing"""
        self.save_settings()
        
        # Close all browser tabs properly
        for i in range(self.tab_manager.count()):
            browser = self.tab_manager.widget(i)
            if browser:
                browser.stop()
                browser.deleteLater()
                
        super().closeEvent(event)
