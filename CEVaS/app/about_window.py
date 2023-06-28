from pathlib import Path

from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PySide6.QtGui import QPixmap, QFont


def get_project_root() -> Path:
    return Path(__file__).parent.parent


class AboutWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('About CEVaS')

        self._drawAboutWindow()

        self.show()

    def _drawAboutWindow(self) -> None:

        cevas_root = get_project_root()
        logo_ceaal_path = Path(cevas_root,'assets','logo_ceaal_transp.png')
        self.pixmap = QPixmap(logo_ceaal_path)

        self.resize(self.pixmap.width()*2, self.pixmap.height())

        horizontal_layout = QHBoxLayout(self)

        lbl_logo = QLabel()
        lbl_logo.setPixmap(self.pixmap)
        lbl_logo.resize(self.pixmap.width(),self.pixmap.height())

        horizontal_layout.addWidget(lbl_logo)

        vertical_layout = QVBoxLayout()
        horizontal_layout.addLayout(vertical_layout)

        lbl_cevas = QLabel()
        lbl_cevas.setText("CEVaS")
        lbl_cevas.setFont(QFont('Times', 16))
        vertical_layout.addWidget(lbl_cevas)

        lbl_description =QLabel()
        lbl_description.setText("CEVas (CEAAL Variable Stars) is a tool to help amateur astronomers measure the magnitude of variable stars.")
        lbl_description.setWordWrap(True)
        vertical_layout.addWidget(lbl_description)

        lbl_developer = QLabel()
        lbl_developer.setText("Developed by:")
        vertical_layout.addWidget(lbl_developer)

        lbl_linkedin = QLabel()
        lbl_linkedin.setText('''<a href='http://www.linkedin.com/in/hfcpeixoto'>Hélvio Peixoto</a>''')
        lbl_linkedin.setOpenExternalLinks(True)
        vertical_layout.addWidget(lbl_linkedin)

        lbl_ceaal = QLabel()
        lbl_ceaal.setText('''<a href='http://www.ceaal.org.br'>CEAAL</a>''')
        lbl_ceaal.setOpenExternalLinks(True)
        vertical_layout.addWidget(lbl_ceaal)

        lbl_github = QLabel()
        lbl_github.setText('''<a href='www.github.com/hfcpeixoto/CEVaS'>Github repo</a>''')
        lbl_github.setOpenExternalLinks(True)
        vertical_layout.addWidget(lbl_github)
