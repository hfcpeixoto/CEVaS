from CEVaS import CEAAL
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
from math import sqrt
import numpy as np


def threshold_star_img(pixel):
    # Grayscale thresold set to 50
    threshold = 50
    return pixel if pixel > threshold else 0


class VariableStarsApp(tk.Frame):
    def initSelectedImage(self):
        if self.selectedImageFrame == "":
            self.selectedImageFrame = tk.Frame(
                self, width=self.resizedImg.width(), height=self.resizedImg.height()
            )
            self.selectedImageCanvas = tk.Canvas(
                self.selectedImageFrame,
                width=self.resizedImg.width(),
                height=self.resizedImg.height(),
            )

        if self.selectedImageId != 0:
            self.selectedImageCanvas.delete(self.selectedImageId)

        self.selectedImageId = self.selectedImageCanvas.create_image(
            0, 0, image=self.resizedImg, anchor=tk.NW
        )
        self.selectedImageCanvas.grid(row=0, column=0)
        self.selectedImageFrame.configure(
            width=self.resizedImg.width(), height=self.resizedImg.height()
        )
        self.selectedImageCanvas.configure(
            width=self.resizedImg.width(), height=self.resizedImg.height()
        )
        self.selectedImageFrame.pack()
        self.pack()

    def pickStar(self, event, star):
        if len(star.imageCross) != 0:
            for i in star.imageCross:
                self.selectedImageCanvas.delete(i)

        star.xPick.set(int(self.canvas1.canvasx(event.x)))
        star.yPick.set(int(self.canvas1.canvasy(event.y)))
        self.top.destroy()
        self.top.update()

        star.evalStarBBox(self.img_gray_array)

        self.img_gray.crop((star.xMin,star.yMin,star.xMax,star.yMax)).show()

        # Mapping click position from full image to resized
        x = int(int(star.xPick.get()) * self.resizedImg.width() / self.pilImg.width)
        y = int(int(star.yPick.get()) * self.resizedImg.height() / self.pilImg.height)

        colour = star.getHexColour()
        star.imageCross.append(
            self.selectedImageCanvas.create_line(
                x, y + 2, x, y + 10, fill=colour, width=3
            )
        )
        star.imageCross.append(
            self.selectedImageCanvas.create_line(
                x - 2, y, x - 10, y, fill=colour, width=3
            )
        )
        star.imageCross.append(
            self.selectedImageCanvas.create_line(
                x, y - 2, x, y - 10, fill=colour, width=3
            )
        )
        star.imageCross.append(
            self.selectedImageCanvas.create_line(
                x + 2, y, x + 10, y, fill=colour, width=3
            )
        )

        self.selectedImageCanvas.pack()
        self.selectedImageFrame.pack()

    def initStarImage(self, star):
        if self.img != "":
            self.top = tk.Toplevel()
            # Open maximized window
            self.top.state("zoomed")
            self.top.title("Pick the star")

            self.canvas1 = tk.Canvas(
                self.top,
                width=self.img.width(),
                height=self.img.height(),
                scrollregion=(0, 0, self.img.width(), self.img.height()),
            )
            self.hbar = tk.Scrollbar(self.top, orient=tk.HORIZONTAL)
            self.hbar.pack(side=tk.BOTTOM, fill=tk.X)
            self.hbar.config(command=self.canvas1.xview)
            self.vbar = tk.Scrollbar(self.top, orient=tk.VERTICAL)
            self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.vbar.config(command=self.canvas1.yview)
            self.canvas1.config(
                xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set
            )
            self.canvas1.create_image(0, 0, image=self.img, anchor="nw")
            self.canvas1.bind("<Button 1>", lambda event: self.pickStar(event, star))
            self.canvas1.bind(
                "<Left>", lambda event: self.canvas1.xview_scroll(-1, "units")
            )
            self.canvas1.bind(
                "<Right>", lambda event: self.canvas1.xview_scroll(1, "units")
            )
            self.canvas1.bind(
                "<Up>", lambda event: self.canvas1.yview_scroll(-1, "units")
            )
            self.canvas1.bind(
                "<Down>", lambda event: self.canvas1.yview_scroll(1, "units")
            )
            self.canvas1.focus_set()
            self.canvas1.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    def initApp(self):
        self.tableFrame = tk.Frame(self)
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

        # Comparison star 1
        star1Lbl = tk.Label(self.tableFrame, text="Comp star 1")
        star1Lbl.grid(row=1, column=0)

        star1PixelxLbl = tk.Label(self.tableFrame, textvariable=self.star1.xPick)
        star1PixelxLbl.grid(row=1, column=1)

        star1PixelyLbl = tk.Label(self.tableFrame, textvariable=self.star1.yPick)
        star1PixelyLbl.grid(row=1, column=2)

        self.star1MagTxt = tk.Entry(self.tableFrame, width=4, text="")
        self.star1MagTxt.grid(row=1, column=3)
        self.star1MagTxt.insert(0, "0.0")

        selectStar1Btn = tk.Button(
            self.tableFrame, text="Pick", command=lambda: self.initStarImage(self.star1)
        )
        selectStar1Btn.grid(row=1, column=4)

        # Comparison star 2
        star2Lbl = tk.Label(self.tableFrame, text="Comp star 2")
        star2Lbl.grid(row=2, column=0)

        star2PixelxLbl = tk.Label(self.tableFrame, textvariable=self.star2.xPick)
        star2PixelxLbl.grid(row=2, column=1)

        star2PixelyLbl = tk.Label(self.tableFrame, textvariable=self.star2.yPick)
        star2PixelyLbl.grid(row=2, column=2)

        self.star2MagTxt = tk.Entry(self.tableFrame, width=4, text="")
        self.star2MagTxt.grid(row=2, column=3)
        self.star2MagTxt.insert(0, "0.0")

        selectStar2Btn = tk.Button(
            self.tableFrame, text="Pick", command=lambda: self.initStarImage(self.star2)
        )
        selectStar2Btn.grid(row=2, column=4)

        # Variable star
        varStarLbl = tk.Label(self.tableFrame, text="Variable star")
        varStarLbl.grid(row=3, column=0)

        varStarPixelxLbl = tk.Label(self.tableFrame, textvariable=self.varStar.xPick)
        varStarPixelxLbl.grid(row=3, column=1)

        star2PixelyLbl = tk.Label(self.tableFrame, textvariable=self.varStar.yPick)
        star2PixelyLbl.grid(row=3, column=2)

        self.varStarMagTxt = tk.Label(
            self.tableFrame, width=4, textvariable=self.varStar.magnitude
        )
        self.varStarMagTxt.grid(row=3, column=3)

        selectVarStarBtn = tk.Button(
            self.tableFrame,
            text="Pick",
            command=lambda: self.initStarImage(self.varStar),
        )
        selectVarStarBtn.grid(row=3, column=4)

        # Select image button
        selectImageBtn = tk.Button(
            self.tableFrame,
            text="Select image",
            width=10,
            height=2,
            command=self.selectImage,
        )
        selectImageBtn.grid(row=0, column=5, rowspan=3)

        # Evaluate magnitude button
        evalMagnitudeBtn = tk.Button(
            self.tableFrame,
            text="Evaluate",
            width=10,
            height=2,
            command=self.evaluateMagnitude,
        )
        evalMagnitudeBtn.grid(row=3, column=5, rowspan=2)

        # Selected image status
        statusSelectedImageLbl = tk.Label(
            self.tableFrame, anchor=tk.W, justify=tk.LEFT, textvariable=self.filename
        )
        statusSelectedImageLbl.grid(row=4, column=0, columnspan=4)


    def evaluateMagnitude(self):
        self.evaluateRelativeLuminance()


    def evaluateRelativeLuminance(self):
        star1RelLum   = self.star1.getAverageRelativeLuminance()
        print(star1RelLum)
        star2RelLum   = self.star2.getAverageRelativeLuminance()
        print(star2RelLum)
        varStarRelLum = self.varStar.getAverageRelativeLuminance()

        star1Mag = float(self.star1MagTxt.get())
        star2Mag = float(self.star2MagTxt.get())
        alpha = (star2Mag - star1Mag) / (star2RelLum - star1RelLum)

        varStarMag = alpha * (varStarRelLum - star1RelLum) + star1Mag
        self.varStar.magnitude.set("{:.2f}".format(varStarMag))

    def selectImage(self):
        self.filename.set(
            tk.filedialog.askopenfilename(
                parent=self.parent, initialdir="./", title="Choose an image."
            )
        )

        self.pilImg = Image.open(self.filename.get())
        self.resizedImg = ImageTk.PhotoImage(
            self.pilImg.resize(
                (
                    self.winfo_width(),
                    int(self.pilImg.height / self.pilImg.width * self.winfo_width()),
                ),
                Image.ANTIALIAS,
            )
        )
        self.img = ImageTk.PhotoImage(self.pilImg)
        self.img_gray = ImageOps.grayscale(self.pilImg)
        self.img_gray = self.img_gray.point(threshold_star_img)
        self.img_gray_array = np.transpose(np.asarray(self.img_gray))

        self.initSelectedImage()

        self.pack()

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        parent.title("Variable star's magnitude evaluator")
        self.parent = parent
        self.selectedImageFrame = ""

        self.filename = tk.StringVar()
        self.filename.set("No image selected.")
        self.img = ""
        self.selectedImageId = 0

        self.star1 = CEAAL.Star(colour=(255, 255, 0))
        self.star2 = CEAAL.Star(colour=(255, 0, 0))
        self.varStar = CEAAL.Star(colour=(255, 0, 255))

        self.initApp()

        self.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = VariableStarsApp(root)
    root.mainloop()
