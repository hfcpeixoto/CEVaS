import tkinter as tk

from CEVaS.app.variable_star_app import VariableStarsApp


from PySide6.QtWidgets import QApplication, QWidget, QMainWindow

app = QApplication()

main_window = VariableStarsApp()
main_window.show()

app.exec()
