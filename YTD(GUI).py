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