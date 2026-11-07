import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5 import uic

class BookLoanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load file .ui yang dibuat dari Qt Designer
        uic.loadUi("peminjamanbuku.ui", self)
        
        # Inisialisasi Database SQLite & Setup Model Tabel
        self.init_db()
        self.setup_models()
        
        # Hubungkan tombol (signal) dengan fungsi (slot)
        self.btn_add.clicked.connect(self.add_book)
        self.btn_pinjam.clicked.connect(self.process_loan)
        self.btn_kembali.clicked.connect(self.return_book)
        self.btn_refresh.clicked.connect(self.refresh_tables)
        
    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("library.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Tidak dapat membuka database!")
            return
        
        query = QSqlQuery()
        # Tabel Buku
        query.exec("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                stock INTEGER
            )
        """)
        # Tabel Peminjaman
        query.exec("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER,
                borrower TEXT,
                loan_date TEXT,
                status TEXT
            )
        """)
        
    def setup_models(self):
        # Model Tabel Kelola Buku
        self.book_model = QSqlTableModel()
        self.book_model.setTable("books")
        self.book_model.select()
        self.book_table.setModel(self.book_model)
        
        # Model Tabel Pengembalian (Hanya pinjaman aktif)
        self.loan_model = QSqlTableModel()
        self.loan_model.setTable("loans")
        self.loan_model.setFilter("status='active'")
        self.loan_model.select()
        self.loan_table.setModel(self.loan_model)
        
        # Model Tabel Laporan (Semua riwayat peminjaman)
        self.report_model = QSqlTableModel()
        self.report_model.setTable("loans")
        self.report_model.select()
        self.report_table.setModel(self.report_model)
        
    def add_book(self):
        if self.title_input.text() and self.stock_input.text():
            record = self.book_model.record()
            record.setValue("title", self.title_input.text())
            record.setValue("author", self.author_input.text())
            record.setValue("stock", int(self.stock_input.text()))
            self.book_model.insertRecord(-1, record)
            self.book_model.select()
            self.title_input.clear()
            self.author_input.clear()
            self.stock_input.clear()
            QMessageBox.information(self, "Sukses", "Buku berhasil ditambahkan!")
            
    def process_loan(self):
        book_id = self.pinjam_book_id.text()
        borrower = self.pinjam_borrower.text()
        if book_id and borrower:
            query = QSqlQuery()
            query.prepare("INSERT INTO loans (book_id, borrower, loan_date, status) VALUES (?, ?, date('now'), 'active')")
            query.addBindValue(int(book_id))
            query.addBindValue(borrower)
            query.exec()
            QMessageBox.information(self, "Sukses", "Peminjaman buku berhasil dicatat!")
            self.pinjam_book_id.clear()
            self.pinjam_borrower.clear()
            self.refresh_tables()
            
    def return_book(self):
        current = self.loan_table.currentIndex()
        if current.isValid():
            row = current.row()
            loan_id = self.loan_model.data(self.loan_model.index(row, 0))
            query = QSqlQuery()
            query.prepare("UPDATE loans SET status='returned' WHERE id=?")
            query.addBindValue(loan_id)
            query.exec()
            self.refresh_tables()
            QMessageBox.information(self, "Sukses", "Buku berhasil dikembalikan!")
            
    def refresh_tables(self):
        self.book_model.select()
        self.loan_model.select()
        self.report_model.select()
        QMessageBox.information(self, "Refresh", "Data laporan berhasil diperbarui!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookLoanApp()
    window.show()
    sys.exit(app.exec_())