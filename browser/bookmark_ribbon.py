from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class BookmarkRibbon(QToolBar):
    bookmark_clicked = pyqtSignal(str)
    
    def __init__(self, bookmark_manager):
        super().__init__()
        self.bookmark_manager = bookmark_manager
        self.setup_ui()
        self.refresh_bookmarks()
        
    def setup_ui(self):
        self.setMovable(False)
        self.setFloatable(False)
        self.setOrientation(Qt.Horizontal)
        
    def refresh_bookmarks(self):
        """Refresh the bookmark buttons"""
        # Clear existing buttons
        self.clear()
        
        # Add bookmark buttons
        bookmarks = self.bookmark_manager.get_bookmarks()
        for bookmark in bookmarks[:10]:  # Show first 10 bookmarks
            btn = QToolButton()
            btn.setText(bookmark['title'][:15] + '...' if len(bookmark['title']) > 15 else bookmark['title'])
            btn.setToolTip(f"{bookmark['title']}\n{bookmark['url']}")
            btn.setMaximumWidth(120)
            btn.clicked.connect(lambda checked, url=bookmark['url']: self.bookmark_clicked.emit(url))
            self.addWidget(btn)
        
        # Add spacer if there are bookmarks
        if bookmarks:
            spacer = QWidget()
            spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.addWidget(spacer)
        
        # Add manage bookmarks button
        manage_btn = QToolButton()
        manage_btn.setText("Manage Bookmarks")
        manage_btn.clicked.connect(self.show_bookmark_manager)
        self.addWidget(manage_btn)
        
    def show_bookmark_manager(self):
        """Show bookmark management dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Bookmarks")
        dialog.setGeometry(200, 200, 500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Bookmark list
        list_widget = QListWidget()
        bookmarks = self.bookmark_manager.get_bookmarks()
        for bookmark in bookmarks:
            list_widget.addItem(f"{bookmark['title']} - {bookmark['url']}")
        
        layout.addWidget(list_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(lambda: self.delete_bookmark(list_widget))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        dialog.exec_()
        
    def delete_bookmark(self, list_widget):
        """Delete selected bookmark"""
        current_row = list_widget.currentRow()
        if current_row >= 0:
            bookmarks = self.bookmark_manager.get_bookmarks()
            if current_row < len(bookmarks):
                bookmark = bookmarks[current_row]
                self.bookmark_manager.remove_bookmark(bookmark['url'])
                self.refresh_bookmarks()
                list_widget.takeItem(current_row)
