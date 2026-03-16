
import sys
from PySide6.QtWidgets import QApplication
from database.db import engine
from database.models import Base
from ui.main_window import MainWindow

def main():
    Base.metadata.create_all(engine)
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1000,600)
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
