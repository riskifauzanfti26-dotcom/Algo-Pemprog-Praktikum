import sys
from PyQt5 import QtWidgets, uic
import db_helper


class LaporanWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(LaporanWindow, self).__init__()
        # Load UI
        uic.loadUi('laporan.ui', self)

        # Connect buttons
        self.btnRefresh.clicked.connect(self.load_report_data)
        self.btnKembali.clicked.connect(self.close)

        # Adjust table headers
        self.tableLaporan.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # Initial data loading
        self.load_report_data()

    def load_report_data(self):
        # Clear existing table data
        self.tableLaporan.setRowCount(0)

        # Fetch all loan transactions from database
        transactions = db_helper.get_all_loans_report()

        for row_number, row_data in enumerate(transactions):
            self.tableLaporan.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                self.tableLaporan.setItem(row_number, column_number, item)