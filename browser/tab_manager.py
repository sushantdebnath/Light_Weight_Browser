from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *

class TabManager(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setTabsClosable(True)
        self.setMovable(True)
        self.tabCloseRequested.connect(self.close_tab)
        
        # Add new tab button
        self.setCornerWidget(self.create_new_tab_button())
        
    def create_new_tab_button(self):
        btn = QToolButton()
        btn.setText('+')
        btn.clicked.connect(self.add_new_tab)
        return btn
        
    def add_tab(self, browser, title):
        """Add a new tab with browser widget"""
        index = self.addTab(browser, title)
        
        # Create close button for tab
        tab_bar = self.tabBar()
        close_btn = QToolButton()
        close_btn.setText('×')
        close_btn.setCursor(Qt.ArrowCursor)
        close_btn.clicked.connect(lambda: self.close_tab(index))
        
        tab_bar.setTabButton(index, QTabBar.RightSide, close_btn)
        
        return index
        
    def add_new_tab(self):
        """Add empty new tab"""
        from .browser_window import BrowserWindow
        parent = self.parent()
        while parent and not isinstance(parent, BrowserWindow):
            parent = parent.parent()
            
        if parent:
            parent.add_new_tab()
            
    def close_tab(self, index):
        """Close tab at specified index"""
        if self.count() > 1:
            widget = self.widget(index)
            if widget:
                widget.deleteLater()
            self.removeTab(index)
            
    def close_current_tab(self):
        """Close currently active tab"""
        current_index = self.currentIndex()
        self.close_tab(current_index)
        
    def set_tab_title(self, browser, title):
        """Set title for tab containing specific browser"""
        for i in range(self.count()):
            if self.widget(i) == browser:
                self.setTabText(i, title[:20] + '...' if len(title) > 20 else title)
                break
