from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
                               QPushButton, QListWidget, QListWidgetItem,
                               QMessageBox, QLabel)
from database.db import Session
from database.models import Parameter


class ParametersDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Správa parametrů")
        self.setMinimumWidth(350)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Existující parametry:"))
        self.list = QListWidget()
        layout.addWidget(self.list)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Název nového parametru (např. Barva)")
        layout.addWidget(self.input)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Přidat")
        self.btn_rename = QPushButton("Přejmenovat")
        self.btn_delete = QPushButton("Smazat")
        self.btn_delete.setStyleSheet("color: #c0392b;")

        self.btn_add.clicked.connect(self.add_parameter)
        self.btn_rename.clicked.connect(self.rename_parameter)
        self.btn_delete.clicked.connect(self.delete_parameter)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_rename)
        btn_layout.addWidget(self.btn_delete)
        layout.addLayout(btn_layout)

        self.list.itemClicked.connect(lambda item: self.input.setText(item.text()))

        self.setLayout(layout)
        self.load_parameters()

    def load_parameters(self):
        session = Session()
        params = session.query(Parameter).order_by(Parameter.name).all()
        session.close()

        self.list.clear()
        for p in params:
            item = QListWidgetItem(p.name)
            item.setData(256, p.id)  # uložíme ID do UserRole
            self.list.addItem(item)

    def add_parameter(self):
        name = self.input.text().strip()
        if not name:
            return

        session = Session()
        exists = session.query(Parameter).filter_by(name=name).first()
        if exists:
            QMessageBox.warning(self, "Duplicita", f"Parametr '{name}' již existuje.")
            session.close()
            return

        session.add(Parameter(name=name))
        session.commit()
        session.close()

        self.input.clear()
        self.load_parameters()

    def rename_parameter(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "Přejmenovat", "Vyberte parametr ze seznamu.")
            return

        new_name = self.input.text().strip()
        if not new_name:
            return

        session = Session()
        param = session.get(Parameter, item.data(256))
        if param:
            param.name = new_name
            session.commit()
        session.close()

        self.input.clear()
        self.load_parameters()

    def delete_parameter(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "Smazat", "Vyberte parametr ze seznamu.")
            return

        confirm = QMessageBox.question(
            self, "Smazat parametr",
            f"Opravdu smazat parametr '{item.text()}'?\nBude odstraněn u všech produktů.",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        session = Session()
        param = session.get(Parameter, item.data(256))
        if param:
            session.delete(param)
            session.commit()
        session.close()

        self.load_parameters()