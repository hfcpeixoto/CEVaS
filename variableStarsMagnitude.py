from CEVaS import CEAAL
from tkinter import *
from tkinter.filedialog import askopenfilename
from PIL import Image, ImageTk
    
class VariableStarsApp(Frame):

    def initSelectedImage(self):
        if self.selectedImageFrame == '':
            self.selectedImageFrame = Frame(self, width=self.resizedImg.width(), height=self.resizedImg.height())
            self.selectedImageCanvas = Canvas(self.selectedImageFrame, width = self.resizedImg.width(), height = self.resizedImg.height())

        if self.selectedImageId != 0:
            self.selectedImageCanvas.delete(self.selectedImageId)

        self.selectedImageId = self.selectedImageCanvas.create_image(0,0,image=self.resizedImg, anchor=NW)
        self.selectedImageCanvas.grid(row=0,column=0)
        self.selectedImageFrame.configure(width=self.resizedImg.width(), height=self.resizedImg.height())
        self.selectedImageCanvas.configure(width=self.resizedImg.width(), height=self.resizedImg.height())
        self.selectedImageFrame.pack()
        self.pack()

    def pickStar(self, event, star):
        if len(star.imageCross) != 0:
            for i in star.imageCross:
                self.selectedImageCanvas.delete(i)

        star.x.set(int(self.canvas1.canvasx(event.x)))
        star.y.set(int(self.canvas1.canvasy(event.y)))
        self.top.destroy()
        self.top.update()

        # Mapping click poosition from full image to resized
        x = int(int(star.x.get())*self.resizedImg.width()/self.pilImg.width)
        y = int(int(star.y.get())*self.resizedImg.height()/self.pilImg.height)

        colour = star.getHexColour()
        star.imageCross.append(self.selectedImageCanvas.create_line( x  , y+2, x   , y+10, fill=colour, width=3))
        star.imageCross.append(self.selectedImageCanvas.create_line( x-2, y  , x-10, y   , fill=colour, width=3))
        star.imageCross.append(self.selectedImageCanvas.create_line( x  , y-2, x   , y-10, fill=colour, width=3))
        star.imageCross.append(self.selectedImageCanvas.create_line( x+2, y  , x+10, y   , fill=colour, width=3))

        self.selectedImageCanvas.pack()
        self.selectedImageFrame.pack()    

    def initStarImage(self, star):
        if self.img != '':
            self.top = Toplevel()
            #Open maximized window
            self.top.state('zoomed')
            self.top.title('Pick the star')

            self.canvas1 = Canvas(self.top, width=self.img.width(), height=self.img.height(),scrollregion=(0,0,self.img.width(),self.img.height()))
            self.hbar=Scrollbar(self.top,orient=HORIZONTAL)
            self.hbar.pack(side=BOTTOM,fill=X)
            self.hbar.config(command=self.canvas1.xview)
            self.vbar=Scrollbar(self.top,orient=VERTICAL)
            self.vbar.pack(side=RIGHT,fill=Y)
            self.vbar.config(command=self.canvas1.yview)
            self.canvas1.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)
            self.canvas1.create_image(0,0,image=self.img,anchor="nw")
            self.canvas1.bind("<Button 1>", lambda event: self.pickStar(event, star))
            self.canvas1.bind("<Left>",  lambda event: self.canvas1.xview_scroll(-1, "units"))
            self.canvas1.bind("<Right>", lambda event: self.canvas1.xview_scroll( 1, "units"))
            self.canvas1.bind("<Up>",    lambda event: self.canvas1.yview_scroll(-1, "units"))
            self.canvas1.bind("<Down>",  lambda event: self.canvas1.yview_scroll( 1, "units"))
            self.canvas1.focus_set()            
            self.canvas1.pack(side=LEFT,expand=True,fill=BOTH)

    def initApp(self):
        self.tableFrame = Frame(self)
        self.tableFrame.pack(side=TOP, anchor=NW)

        starsHeaderLbl = Label(self.tableFrame, text="Stars")
        starsHeaderLbl.grid(row=0, column=0)

        starsHeaderLbl = Label(self.tableFrame, text="x-Pixel")
        starsHeaderLbl.grid(row=0, column=1)

        starsHeaderLbl = Label(self.tableFrame, text="y-Pixel")
        starsHeaderLbl.grid(row=0, column=2)

        starsHeaderLbl = Label(self.tableFrame, text="Magnitude")
        starsHeaderLbl.grid(row=0, column=3)

        starsHeaderLbl = Label(self.tableFrame, text="Pick from image")
        starsHeaderLbl.grid(row=0, column=4)

        #Comparison star 1
        star1Lbl = Label(self.tableFrame, text="Comp star 1")
        star1Lbl.grid(row=1, column=0)

        star1PixelxLbl = Label(self.tableFrame, textvariable=self.star1.x)
        star1PixelxLbl.grid(row=1, column=1)

        star1PixelyLbl = Label(self.tableFrame, textvariable=self.star1.y)
        star1PixelyLbl.grid(row=1, column=2)

        self.star1MagTxt = Entry(self.tableFrame, width=4, text="")
        self.star1MagTxt.grid(row=1, column=3)
        self.star1MagTxt.insert(0,"0.0")

        selectStar1Btn = Button(self.tableFrame, text="Pick", command=lambda: self.initStarImage(self.star1))
        selectStar1Btn.grid(row=1, column=4)

        #Comparison star 2
        star2Lbl = Label(self.tableFrame, text="Comp star 2")
        star2Lbl.grid(row=2, column=0)

        star2PixelxLbl = Label(self.tableFrame, textvariable=self.star2.x)
        star2PixelxLbl.grid(row=2, column=1)

        star2PixelyLbl = Label(self.tableFrame, textvariable=self.star2.y)
        star2PixelyLbl.grid(row=2, column=2)

        self.star2MagTxt = Entry(self.tableFrame, width=4, text="")
        self.star2MagTxt.grid(row=2, column=3)
        self.star2MagTxt.insert(0,"0.0")

        selectStar2Btn = Button(self.tableFrame, text="Pick", command=lambda: self.initStarImage(self.star2))
        selectStar2Btn.grid(row=2, column=4)

        #Variable star
        varStarLbl = Label(self.tableFrame, text="Variable star")
        varStarLbl.grid(row=3, column=0)

        varStarPixelxLbl = Label(self.tableFrame, textvariable=self.varStar.x)
        varStarPixelxLbl.grid(row=3, column=1)

        star2PixelyLbl = Label(self.tableFrame, textvariable=self.varStar.y)
        star2PixelyLbl.grid(row=3, column=2)

        self.varStarMagTxt = Label(self.tableFrame, width=4, textvariable=self.varStar.magnitude)
        self.varStarMagTxt.grid(row=3, column=3)

        selectVarStarBtn = Button(self.tableFrame, text="Pick", command=lambda: self.initStarImage(self.varStar))
        selectVarStarBtn.grid(row=3, column=4)

        #Select image button
        selectImageBtn = Button(self.tableFrame, text="Select image", width=10, height=2, command=self.selectImage)
        selectImageBtn.grid(row=0, column=5, rowspan=3)

        #Select image button
        evalMagnitudeBtn = Button(self.tableFrame, text="Evaluate", width=10, height=2, command=self.evaluateRelativeLuminance)
        evalMagnitudeBtn.grid(row=3, column=5, rowspan=2)

        #Selected image status
        statusSelectedImageLbl = Label(self.tableFrame, anchor=W, justify=LEFT, textvariable=self.filename)
        statusSelectedImageLbl.grid(row=4, column=0, columnspan=4)

    

    def evaluateRelativeLuminance(self):
        #https://en.wikipedia.org/wiki/Relative_luminance
        pix=self.pilImg.load()
        self.star1.pixelRBG = pix[int(self.star1.x.get()),int(self.star1.y.get())]
        star1RelLum = self.star1.getRelativeLuminance()
        self.star2.pixelRBG = pix[int(self.star2.x.get()),int(self.star2.y.get())]
        star2RelLum = self.star2.getRelativeLuminance()
        self.varStar.pixelRBG = pix[int(self.varStar.x.get()),int(self.varStar.y.get())]
        varStarRelLum = self.varStar.getRelativeLuminance()

        star1Mag = float(self.star1MagTxt.get())
        star2Mag = float(self.star2MagTxt.get())
        alpha = (star2Mag-star1Mag)/(star2RelLum-star1RelLum)

        varStarMag = alpha*(varStarRelLum-star1RelLum)+star1Mag
        self.varStar.magnitude.set("{:.2f}".format(varStarMag))
        
    def selectImage(self):
        self.filename.set(askopenfilename(parent=self.parent, initialdir="./",title='Choose an image.'))
        
        self.pilImg = Image.open(self.filename.get())
        self.resizedImg = ImageTk.PhotoImage(self.pilImg.resize((self.winfo_width(), int(self.pilImg.height/self.pilImg.width*self.winfo_width())), Image.ANTIALIAS))
        self.img = ImageTk.PhotoImage(self.pilImg)
        
        self.initSelectedImage()

        self.pack()

    def __init__(self, parent):
        Frame.__init__(self, parent)
        parent.title("Variable star's magnitude evaluator")
        self.parent = parent
        self.selectedImageFrame = ''

        self.filename = StringVar()
        self.filename.set("No image selected.")
        self.img = ''
        self.selectedImageId = 0

        self.star1   = CEAAL.Star(colour=(255,255,0  ))
        self.star2   = CEAAL.Star(colour=(255,0  ,0  ))
        self.varStar = CEAAL.Star(colour=(255,0  ,255))

        self.initApp()

        self.pack()


if __name__ == "__main__":
    root = Tk()

    app = VariableStarsApp(root)

    root.mainloop()
    