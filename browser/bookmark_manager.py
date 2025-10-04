import json
import os

class BookmarkManager:
    def __init__(self):
        self.bookmarks_file = "bookmarks.json"
        self.bookmarks = self.load_bookmarks()
        
    def load_bookmarks(self):
        try:
            if os.path.exists(self.bookmarks_file):
                with open(self.bookmarks_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
        
    def save_bookmarks(self):
        try:
            with open(self.bookmarks_file, 'w') as f:
                json.dump(self.bookmarks, f, indent=2)
        except:
            pass
            
    def add_bookmark(self, url, title):
        bookmark = {'url': url, 'title': title}
        
        if not any(b['url'] == url for b in self.bookmarks):
            self.bookmarks.append(bookmark)
            self.save_bookmarks()
            return True
        return False
        
    def remove_bookmark(self, url):
        self.bookmarks = [b for b in self.bookmarks if b['url'] != url]
        self.save_bookmarks()
        
    def toggle_bookmark(self, url, title):
        if any(b['url'] == url for b in self.bookmarks):
            self.remove_bookmark(url)
            return False
        else:
            self.add_bookmark(url, title)
            return True
            
    def get_bookmarks(self):
        return self.bookmarks.copy()
