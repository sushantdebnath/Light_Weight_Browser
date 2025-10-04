from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class NavigationBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        main_layout = QVBoxLayout(self)  # Set layout to self directly
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create horizontal layout for buttons and URL bar
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(5, 5, 5, 5)
        nav_layout.setSpacing(5)
        
        # Back button
        self.back_btn = QToolButton()
        self.back_btn.setText('←')
        self.back_btn.setToolTip('Back')
        
        # Forward button
        self.forward_btn = QToolButton()
        self.forward_btn.setText('→')
        self.forward_btn.setToolTip('Forward')
        
        # Reload button
        self.reload_btn = QToolButton()
        self.reload_btn.setText('⟳')
        self.reload_btn.setToolTip('Reload')
        
        # Home button
        self.home_btn = QToolButton()
        self.home_btn.setText('⌂')
        self.home_btn.setToolTip('Home')
        
        # Bookmark button
        self.bookmark_btn = QToolButton()
        self.bookmark_btn.setText('☆')
        self.bookmark_btn.setToolTip('Bookmark this page')
        
        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL or search...")
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setVisible(False)
        
        # Add widgets to horizontal layout
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.home_btn)
        nav_layout.addWidget(self.bookmark_btn)
        nav_layout.addWidget(self.url_bar, 1)  # Stretch factor 1
        
        # Add to main layout
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.progress_bar)
        
    def update_load_progress(self, progress):
        """Update progress bar visibility and value"""
        if progress == 0:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(progress)
