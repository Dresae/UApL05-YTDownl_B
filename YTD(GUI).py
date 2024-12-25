import sys
import yt_dlp
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLineEdit, QPushButton, QComboBox, 
                            QLabel, QProgressBar, QMessageBox, QFileDialog)
from PyQt6.QtCore import QThread, pyqtSignal

# Worker thread for handling downloads without freezing the GUI
class DownloadWorker(QThread):
    
    progress = pyqtSignal(float)
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, url, format_choice, directory):
        super().__init__()
        self.url = url
        self.format_choice = format_choice
        self.directory = directory
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0')
            try:
                percentage = float(p.replace('%',''))
                self.progress.emit(percentage)
            except:
                pass
                
    def run(self):
        try:
            format_selection = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]' if self.format_choice == 'Video (MP4)' else 'bestaudio[ext=m4a]'
            
            ydl_opts = {
                'format': format_selection,
                'progress_hooks': [self.progress_hook],
                'outtmpl': f'{self.directory}/%(title)s.%(ext)s'
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class YTDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setMinimumWidth(500)
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # URL input
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter YouTube URL")
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Download Directory")
        self.dir_button = QPushButton("Browse")
        self.dir_button.clicked.connect(self.select_directory)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        layout.addLayout(dir_layout)
        
        # Format selection
        format_layout = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Video (MP4)", "Audio (M4A)"])
        format_layout.addWidget(QLabel("Format:"))
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)