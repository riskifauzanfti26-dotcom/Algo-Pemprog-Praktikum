import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar
from PyQt5.QtCore import QTimer, Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
        self.setGeometry(300, 300, 500, 300)
        
        layout = QVBoxLayout()
        self.label = QLabel("Welcome to the Main Application!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.label)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading...")
        self.setFixedSize(400, 200)
        # Membuat jendela tanpa border ala splash screen
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout()
        
        self.status_label = QLabel("Loading data...", self)
        self.progress = QProgressBar(self)
        self.progress.setValue(0)
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        self.setLayout(layout)
        
        self.counter = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30) # Kecepatan loading (30 ms)
        
    def update_progress(self):
        self.counter += 1
        self.progress.setValue(self.counter)
        
        # Simulasi teks status berdasarkan persentase
        if self.counter == 50:
            self.status_label.setText("Connecting to database...")
        elif self.counter == 80:
            self.status_label.setText("Preparing interface...")
            
        # Jika loading selesai (mencapai 100)
        if self.counter >= 100:
            self.timer.stop()
            self.main_window = MainWindow()
            self.main_window.show()
            self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Menampilkan splash screen sebelum aplikasi utama dijalankan
    splash = SplashScreen()
    splash.show()
    
    sys.exit(app.exec_())