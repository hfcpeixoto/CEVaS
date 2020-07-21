from tkinter import StringVar
import numpy as np


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
        self.xMin = None
        self.xMax = None
        self.yMin = None
        self.yMax = None
        self.imgArray = None

    def getHexColour(self):
        return "#%02x%02x%02x" % self.colour

    def getRelativeLuminance(self):
        return (
            0.2126 * self.pixelRBG[0]
            + 0.7152 * self.pixelRBG[1]
            + 0.0722 * self.pixelRBG[2]
        )


    def getAverageRelativeLuminance(self):
        img = self.imgArray[self.imgArray!=0]
        img = np.divide(img, 255.)

        return np.mean(img)


    def evalStarBBox(self, img_array):
        xp = int(self.xPick.get())
        yp = int(self.yPick.get())

        xMin = xp
        xMax = xp
        yMin = yp
        yMax = yp

        grayPixel = True
        while grayPixel:
            if img_array[xMin,yp] == 0:
                break
            xMin -= 1

        while grayPixel:
            if img_array[xMax,yp] == 0:
                break
            xMax += 1

        while grayPixel:
            if img_array[xp,yMin] == 0:
                break
            yMin -= 1

        while grayPixel:
            if img_array[xp,yMax] == 0:
                break
            yMax += 1

        xl = xMax - xMin
        yl = yMax - yMin
        xOffset = np.ceil(xl*1.)
        yOffset = np.ceil(yl*1.)

        self.xMin = xMin - xOffset
        self.xMax = xMax + xOffset
        self.yMin = yMin - yOffset
        self.yMax = yMax + yOffset

        self.imgArray = img_array[xMin:xMax,yMin:yMax]

        return