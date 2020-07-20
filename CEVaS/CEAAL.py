from tkinter import StringVar
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk


class Star:
    def __init__(self, colour=(0, 0, 0)):
        self.imageCross = list()
        self.xPick = StringVar()
        self.xPick.set("0")
        self.yPick = StringVar()
        self.yPick.set("0")
        self.magnitude = StringVar()
        self.magnitude.set("0")
        self.colour = colour
        self.pixelRBG = list()

    def getHexColour(self):
        return "#%02x%02x%02x" % self.colour

    def getRelativeLuminance(self):
        return (
            0.2126 * self.pixelRBG[0]
            + 0.7152 * self.pixelRBG[1]
            + 0.0722 * self.pixelRBG[2]
        )
