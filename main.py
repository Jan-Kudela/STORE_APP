import sys

from PySide6.QtWidgets import QApplication

from database import engine
from models import Base
from ui.main_window import MainWindow

Base.metadata.create_all(engine)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())