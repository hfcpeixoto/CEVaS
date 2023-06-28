import tkinter as tk
import webbrowser
from PIL import Image, ImageTk
from CEVaS.model.model import Model
from CEVaS.app.about_window import AboutWindow


from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent


from PySide6.QtWidgets import QMainWindow


class VariableStarsApp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("CEVaS (CEAAL Variable Stars)")
        
        #self._model = Model()
        self._about_window = None
        
        self._initApp()


    def _initApp(self) -> None:
        menubar = self.menuBar()
        
        menubar.addAction("&About", self._openAboutWindow)


        # self._drawApp()

    def _drawApp(self) -> None:
        self.tableFrame = tk.LabelFrame(self)
        self.tableFrame.pack(side=tk.TOP, anchor=tk.NW)

        starsHeaderLbl = tk.Label(self.tableFrame, text="Stars")
        starsHeaderLbl.grid(row=0, column=0)

        starsHeaderLbl = tk.Label(self.tableFrame, text="x-Pixel")
        starsHeaderLbl.grid(row=0, column=1)

        starsHeaderLbl = tk.Label(self.tableFrame, text="y-Pixel")
        starsHeaderLbl.grid(row=0, column=2)

        starsHeaderLbl = tk.Label(self.tableFrame, text="Magnitude")
        starsHeaderLbl.grid(row=0, column=3)

        starsHeaderLbl = tk.Label(self.tableFrame, text="Pick from image")
        starsHeaderLbl.grid(row=0, column=4)

        pickedStarsHeaderLbl = tk.Label(self.tableFrame, text="Picked star")
        pickedStarsHeaderLbl.grid(row=0, column=5)

        # Comparison star 1
        star1Lbl = tk.Label(self.tableFrame, text="Comp star 1")
        star1Lbl.grid(row=1, column=0)

        star1PixelxLbl = tk.Label(self.tableFrame, textvariable=self._model.star1.xPick)
        star1PixelxLbl.grid(row=1, column=1)

        star1PixelyLbl = tk.Label(self.tableFrame, textvariable=self._model.star1.yPick)
        star1PixelyLbl.grid(row=1, column=2)

        self.star1MagTxt = tk.Entry(self.tableFrame, width=4, text="")
        self.star1MagTxt.grid(row=1, column=3)
        self.star1MagTxt.insert(0, "0.0")

        selectStar1Btn = tk.Button(self.tableFrame, text="Pick")
        selectStar1Btn.configure(command=self.initStarImage(self.star1))        
        selectStar1Btn.grid(row=1, column=4)

        self._model.star1.croppedImageLbl = tk.Label(self.tableFrame)
        self._model.star1.croppedImageLbl.grid(row=1, column=5)

        # Comparison star 2
        star2Lbl = tk.Label(self.tableFrame, text="Comp star 2")
        star2Lbl.grid(row=2, column=0)

        star2PixelxLbl = tk.Label(self.tableFrame, textvariable=self._model.star2.xPick)        
        star2PixelxLbl.grid(row=2, column=1)

        star2PixelyLbl = tk.Label(self.tableFrame, textvariable=self._model.star2.yPick)
        star2PixelyLbl.grid(row=2, column=2)

        self.star2MagTxt = tk.Entry(self.tableFrame, width=4, text="")
        self.star2MagTxt.grid(row=2, column=3)
        self.star2MagTxt.insert(0, "0.0")

        selectStar2Btn = tk.Button(self.tableFrame, text="Pick")
        selectStar2Btn.configure(command=lambda: self.initStarImage(self.star2))
        selectStar2Btn.grid(row=2, column=4)

        self._model.star2.croppedImageLbl = tk.Label(self.tableFrame)
        self._model.star2.croppedImageLbl.grid(row=2, column=5)

        # Variable star
        varStarLbl = tk.Label(self.tableFrame, text="Variable star")
        varStarLbl.grid(row=3, column=0)

        varStarPixelxLbl = tk.Label(self.tableFrame)
        varStarPixelxLbl.configure(textvariable=self._model.varStar.xPick)
        varStarPixelxLbl.grid(row=3, column=1)

        star2PixelyLbl = tk.Label(self.tableFrame, textvariable=self._model.varStar.yPick)
        star2PixelyLbl.grid(row=3, column=2)

        self.varStarMagTxt = tk.Label(
            self.tableFrame, width=4, textvariable=self._model.varStar.magnitude
        )
        self.varStarMagTxt.grid(row=3, column=3)

        selectVarStarBtn = tk.Button(
            self.tableFrame,
            text="Pick")
        selectVarStarBtn.configure(command=lambda: self.initStarImage(self.varStar))
        selectVarStarBtn.grid(row=3, column=4)

        self._model.varStar.croppedImageLbl = tk.Label(self.tableFrame)
        self._model.varStar.croppedImageLbl.grid(row=3, column=5)

        # Select image button
        selectImageBtn = tk.Button(
            self.tableFrame,
            text="Select image",
            width=10,
            height=2,)
        selectImageBtn.configure(command=self.selectImage)
        selectImageBtn.grid(row=0, column=6, rowspan=3)

        # Evaluate magnitude button
        evalMagnitudeBtn = tk.Button(
            self.tableFrame,
            text="Evaluate",
            width=10,
            height=2,)
        evalMagnitudeBtn.configure(command=self.evaluateMagnitude)
        evalMagnitudeBtn.grid(row=3, column=6, rowspan=2)

        # Selected image status
        statusSelectedImageLbl = tk.Label(
            self.tableFrame, anchor=tk.W, justify=tk.LEFT, textvariable=self._model.filename
        )
        statusSelectedImageLbl.grid(row=4, column=0, columnspan=6)

    def _openAboutWindow(self) -> None:
        if self._about_window is None or not self._about_window.isActiveWindow():
            self._about_window = AboutWindow()
        
    