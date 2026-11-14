import sys 
from PyQt5.QtWidgets import * 
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel 
from PyQt5.QtCore import Qt, QDate 
 
class LibrarySystem(QMainWindow): 
    def __init__(self): 
        super().__init__() 
        self.setWindowTitle("Sistem Peminjaman Buku") 
        self.setGeometry(300, 300, 900, 600) 
         
        self.init_db() 
        self.setup_ui() 
     
    def init_db(self): 
        self.db = QSqlDatabase.addDatabase("QSQLITE") 
        self.db.setDatabaseName("library.db") 
        self.db.open() 
         
        self.db.exec(""" 
            CREATE TABLE IF NOT EXISTS books ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT NOT NULL, 
                author TEXT, 
                stock INTEGER DEFAULT 1 
            ) 
        """) 
         
        self.db.exec(""" 
            CREATE TABLE IF NOT EXISTS loans ( 
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                book_id INTEGER, 
                borrower TEXT, 
                loan_date TEXT, 
                return_date TEXT, 
                status TEXT DEFAULT 'active' 
            ) 
        """) 
     
    def setup_ui(self): 
        # Tab widget 
        tabs = QTabWidget() 
        self.setCentralWidget(tabs) 
         
        # Tab 1: Manage Books 
        books_tab = QWidget() 
        tabs.addTab(books_tab, "Kelola Buku") 
         
        books_layout = QVBoxLayout(books_tab) 
         
        # Book form 
        form_layout = QGridLayout() 
        self.title_input = QLineEdit() 
        self.author_input = QLineEdit() 
        self.stock_input = QSpinBox() 
        self.stock_input.setRange(1, 100) 
         
        form_layout.addWidget(QLabel("Judul:"), 0, 0) 
        form_layout.addWidget(self.title_input, 0, 1) 
        form_layout.addWidget(QLabel("Penulis:"), 1, 0) 
        form_layout.addWidget(self.author_input, 1, 1) 
        form_layout.addWidget(QLabel("Stok:"), 2, 0) 
        form_layout.addWidget(self.stock_input, 2, 1) 
         
        btn_layout = QHBoxLayout() 
        self.add_book_btn = QPushButton("Tambah Buku") 
        self.update_book_btn = QPushButton("Update Buku") 
        self.delete_book_btn = QPushButton("Hapus Buku") 
        btn_layout.addWidget(self.add_book_btn) 
        btn_layout.addWidget(self.update_book_btn) 
        btn_layout.addWidget(self.delete_book_btn) 
         
        # Book table 
        self.book_model = QSqlTableModel() 
        self.book_model.setTable("books") 
        self.book_model.select() 
        self.book_table = QTableView() 
        self.book_table.setModel(self.book_model) 
        self.book_table.setSelectionBehavior(QTableView.SelectRows) 
         
        books_layout.addLayout(form_layout) 
        books_layout.addLayout(btn_layout) 
        books_layout.addWidget(self.book_table) 
         
        # Tab 2: Borrow Book 
        borrow_tab = QWidget() 
        tabs.addTab(borrow_tab, "Pinjam Buku") 
         
        borrow_layout = QVBoxLayout(borrow_tab) 
         
        # Book selection 
        borrow_layout.addWidget(QLabel("Pilih Buku:")) 
        self.book_combo = QComboBox() 
        self.load_books_to_combo() 
        borrow_layout.addWidget(self.book_combo) 
         
        borrow_layout.addWidget(QLabel("Nama Peminjam:")) 
        self.borrower_input = QLineEdit() 
        borrow_layout.addWidget(self.borrower_input) 
         
        self.borrow_btn = QPushButton("Pinjam Buku") 
        self.borrow_btn.clicked.connect(self.borrow_book) 
        borrow_layout.addWidget(self.borrow_btn) 
         
        # Tab 3: Return Book 
        return_tab = QWidget() 
        tabs.addTab(return_tab, "Kembalikan Buku") 
         
        return_layout = QVBoxLayout(return_tab) 
         
        self.loan_model = QSqlTableModel() 
        self.loan_model.setTable("loans") 
        self.loan_model.setFilter("status='active'") 
        self.loan_model.select() 
        self.loan_table = QTableView() 
        self.loan_table.setModel(self.loan_model) 
        self.loan_table.setSelectionBehavior(QTableView.SelectRows) 
         
        self.return_btn = QPushButton("Kembalikan Buku") 
        self.return_btn.clicked.connect(self.return_book) 
         
        return_layout.addWidget(QLabel("Peminjaman Aktif:")) 
        return_layout.addWidget(self.loan_table) 
        return_layout.addWidget(self.return_btn) 
         
        # Tab 4: Reports 
        reports_tab = QWidget() 
        tabs.addTab(reports_tab, "Laporan") 
         
        reports_layout = QVBoxLayout(reports_tab) 
         
        self.stats_label = QLabel() 
        self.stats_label.setAlignment(Qt.AlignTop) 
        self.refresh_btn = QPushButton("Refresh Laporan") 
        self.refresh_btn.clicked.connect(self.refresh_stats) 
         
        reports_layout.addWidget(self.stats_label) 
        reports_layout.addWidget(self.refresh_btn) 
         
        # Signal connections 
        self.add_book_btn.clicked.connect(self.add_book) 
        self.update_book_btn.clicked.connect(self.update_book) 
        self.delete_book_btn.clicked.connect(self.delete_book) 
        self.book_table.clicked.connect(self.on_book_select) 
         
        self.refresh_stats() 
     
    def load_books_to_combo(self): 
        self.book_combo.clear() 
        query = self.db.exec("SELECT id, title FROM books WHERE stock > 0") 
        while query.next(): 
            self.book_combo.addItem(f"{query.value(1)}", query.value(0)) 
     
    def add_book(self): 
        if self.title_input.text(): 
            self.db.exec(f""" 
                INSERT INTO books (title, author, stock) 
                VALUES ('{self.title_input.text()}',  
                        '{self.author_input.text()}',  
                        {self.stock_input.value()}) 
            """) 
            self.book_model.select() 
            self.load_books_to_combo() 
            self.clear_book_form() 
     
    def update_book(self): 
        current = self.book_table.currentIndex() 
        if current.isValid(): 
            row = current.row() 
            book_id = self.book_model.data(self.book_model.index(row, 0)) 
            self.db.exec(f""" 
                UPDATE books  
                SET title='{self.title_input.text()}', 
                    author='{self.author_input.text()}', 
                    stock={self.stock_input.value()} 
                WHERE id={book_id} 
            """) 
            self.book_model.select() 
            self.load_books_to_combo() 
     
    def delete_book(self): 
        current = self.book_table.currentIndex() 
        if current.isValid(): 
            reply = QMessageBox.question(self, "Konfirmasi", "Hapus buku ini?", 
                                        QMessageBox.Yes | QMessageBox.No) 
            if reply == QMessageBox.Yes: 
                row = current.row() 
                book_id = self.book_model.data(self.book_model.index(row, 0)) 
                self.db.exec(f"DELETE FROM books WHERE id={book_id}") 
                self.book_model.select() 
                self.load_books_to_combo() 
     
    def on_book_select(self, index): 
        row = index.row() 
        self.title_input.setText(self.book_model.data(self.book_model.index(row, 1))) 
        self.author_input.setText(self.book_model.data(self.book_model.index(row, 2))) 
        self.stock_input.setValue(int(self.book_model.data(self.book_model.index(row, 3)))) 
     
    def clear_book_form(self): 
        self.title_input.clear() 
        self.author_input.clear() 
        self.stock_input.setValue(1) 
     
    def borrow_book(self): 
        book_id = self.book_combo.currentData() 
        borrower = self.borrower_input.text() 
         
        if borrower and book_id: 
            today = QDate.currentDate().toString("yyyy-MM-dd") 
            self.db.exec(f""" 
                INSERT INTO loans (book_id, borrower, loan_date, status) 
                VALUES ({book_id}, '{borrower}', '{today}', 'active') 
            """) 
            self.db.exec(f"UPDATE books SET stock = stock - 1 WHERE id={book_id}") 
             
            self.book_model.select() 
            self.loan_model.select() 
            self.load_books_to_combo() 
            self.borrower_input.clear() 
            self.refresh_stats() 
             
            QMessageBox.information(self, "Sukses", f"Buku dipinjam oleh {borrower}") 
     
    def return_book(self): 
        current = self.loan_table.currentIndex() 
        if current.isValid(): 
            row = current.row() 
            loan_id = self.loan_model.data(self.loan_model.index(row, 0)) 
            book_id = self.loan_model.data(self.loan_model.index(row, 1)) 
            today = QDate.currentDate().toString("yyyy-MM-dd") 
             
            self.db.exec(f""" 
                UPDATE loans  
                SET return_date='{today}', status='returned'  
                WHERE id={loan_id} 
            """) 
            self.db.exec(f"UPDATE books SET stock = stock + 1 WHERE id={book_id}") 
             
            self.book_model.select() 
            self.loan_model.select() 
            self.load_books_to_combo() 
            self.refresh_stats() 
             
            QMessageBox.information(self, "Sukses", "Buku telah dikembalikan") 
     
    def refresh_stats(self): 
        # Count books 
        query = self.db.exec("SELECT COUNT(*) FROM books") 
        query.next() 
        total_books = query.value(0) 
         
        # Count active loans 
        query = self.db.exec("SELECT COUNT(*) FROM loans WHERE status='active'") 
        query.next() 
        active_loans = query.value(0) 
         
        self.stats_label.setText(f""" 
            <h2>Laporan Perpustakaan</h2> 
            <p><b>Total Buku:</b> {total_books}</p> 
            <p><b>Buku Dipinjam:</b> {active_loans}</p> 
            <p><b>Buku Tersedia:</b> {total_books - active_loans}</p> 
        """) 

if __name__ == "__main__": 
    app = QApplication(sys.argv) 
    window = LibrarySystem() 
    window.show() 
    sys.exit(app.exec_())