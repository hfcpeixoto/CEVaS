import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QAction,
    QMenuBar,
    QStatusBar,
    QGraphicsView,
    QGraphicsScene,
    QFileDialog,
    QDialog,
    QScrollArea, # Though QGraphicsView handles scrolling itself
    QMessageBox
)
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPainter, QColor, QPen, QDesktopServices
from PyQt5.QtCore import Qt, QPointF, QUrl

from CEVaS import CEAAL
import numpy as np
from PIL import Image, ImageOps


def threshold_star_img(pixel_value):
    # Grayscale threshold set to 50
    threshold = 50
    return pixel_value if pixel_value > threshold else 0

# def linkCallback(url): # Not used currently
#     # webbrowser.open_new(url)
#     pass

class PickStarDialog(QDialog):
    def __init__(self, parent, full_image_pixmap, star_name_label):
        super().__init__(parent)
        self.setWindowTitle(f"Pick {star_name_label}")
        self.full_image_pixmap = full_image_pixmap
        self.picked_x = 0
        self.picked_y = 0

        layout = QVBoxLayout(self)
        
        self.instructionsLbl = QLabel(f"Click on the {star_name_label} to select its position.")
        layout.addWidget(self.instructionsLbl)

        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)
        self.scene.addPixmap(self.full_image_pixmap)
        
        self.view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setRenderHint(QPainter.SmoothPixmapTransform)
        # Ensure the view can be large enough for the image
        self.view.setMinimumSize(
            min(800, self.full_image_pixmap.width() + 2 * self.view.frameWidth()), 
            min(600, self.full_image_pixmap.height() + 2 * self.view.frameWidth())
        )

        layout.addWidget(self.view)
        
        # Ok and Cancel buttons are added by default by QDialog? 
        # If not, add them:
        # buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self)
        # buttons.accepted.connect(self.accept)
        # buttons.rejected.connect(self.reject)
        # layout.addWidget(buttons)

        self.view.mousePressEvent = self.handleMouseClick # Override mousePressEvent

    def handleMouseClick(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.view.mapToScene(event.pos())
            self.picked_x = int(scene_pos.x())
            self.picked_y = int(scene_pos.y())
            self.accept() # Closes the dialog and returns QDialog.Accepted

class VariableStarsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CEVaS (CEAAL Variable Stars) - PyQt5")
        self.setGeometry(100, 100, 1200, 800) # x, y, width, height

        self.star1 = CEAAL.Star(colour=(255, 255, 0)) # Yellow
        self.star2 = CEAAL.Star(colour=(255, 0, 0))   # Red
        self.varStar = CEAAL.Star(colour=(255, 0, 255)) # Magenta
        
        self.filename = "No image selected."
        self.pilImg = None 
        self.qtImg = None  # Original QPixmap for display (with crosshairs)
        self.baseQtImg = None # Original QPixmap without crosshairs
        self.img_gray_array = None # Numpy array of grayscaled PIL image

        self._createMenuBar()
        self._initUI()

    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu("&File")
        openAction = QAction("&Open Image...", self)
        openAction.triggered.connect(self.selectImage) # Connect
        fileMenu.addAction(openAction)
        saveAction = QAction("&Save Data...", self)
        saveAction.triggered.connect(self.saveData) # Connect
        fileMenu.addAction(saveAction)
        fileMenu.addSeparator()
        exitAction = QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        helpMenu = menuBar.addMenu("&Help")
        aboutAction = QAction("&About", self)
        aboutAction.triggered.connect(self.openAboutWindow) # Connect
        helpMenu.addAction(aboutAction)

    def _initUI(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        mainLayout = QVBoxLayout(self.centralWidget)

        starTableGroupBox = QWidget() 
        starTableLayout = QGridLayout(starTableGroupBox)
        headers = ["Stars", "x-Pixel", "y-Pixel", "Magnitude", "Pick from image", "Picked star"]
        for col, header_text in enumerate(headers):
            starTableLayout.addWidget(QLabel(header_text), 0, col)

        # Star 1
        starTableLayout.addWidget(QLabel("Comp star 1"), 1, 0)
        self.star1_xPickLbl = QLabel(self.star1.xPick)
        self.star1_yPickLbl = QLabel(self.star1.yPick)
        self.star1_magEdit = QLineEdit("0.0")
        self.star1_pickBtn = QPushButton("Pick")
        self.star1_imgLbl = QLabel() # For cropped image
        self.star1_imgLbl.setFixedSize(64, 64) # Example size
        
        starTableLayout.addWidget(self.star1_xPickLbl, 1, 1)
        starTableLayout.addWidget(self.star1_yPickLbl, 1, 2)
        starTableLayout.addWidget(self.star1_magEdit, 1, 3)
        starTableLayout.addWidget(self.star1_pickBtn, 1, 4)
        starTableLayout.addWidget(self.star1_imgLbl, 1, 5)
        self.star1_pickBtn.clicked.connect(lambda: self.initStarImage(self.star1, "Comparison Star 1"))

        # Star 2
        starTableLayout.addWidget(QLabel("Comp star 2"), 2, 0)
        self.star2_xPickLbl = QLabel(self.star2.xPick)
        self.star2_yPickLbl = QLabel(self.star2.yPick)
        self.star2_magEdit = QLineEdit("0.0")
        self.star2_pickBtn = QPushButton("Pick")
        self.star2_imgLbl = QLabel()
        self.star2_imgLbl.setFixedSize(64, 64)
        
        starTableLayout.addWidget(self.star2_xPickLbl, 2, 1)
        starTableLayout.addWidget(self.star2_yPickLbl, 2, 2)
        starTableLayout.addWidget(self.star2_magEdit, 2, 3)
        starTableLayout.addWidget(self.star2_pickBtn, 2, 4)
        starTableLayout.addWidget(self.star2_imgLbl, 2, 5)
        self.star2_pickBtn.clicked.connect(lambda: self.initStarImage(self.star2, "Comparison Star 2"))

        # Variable Star
        starTableLayout.addWidget(QLabel("Variable star"), 3, 0)
        self.varStar_xPickLbl = QLabel(self.varStar.xPick)
        self.varStar_yPickLbl = QLabel(self.varStar.yPick)
        self.varStar_magLbl = QLabel(self.varStar.magnitude) 
        self.varStar_pickBtn = QPushButton("Pick")
        self.varStar_imgLbl = QLabel()
        self.varStar_imgLbl.setFixedSize(64, 64)
        
        starTableLayout.addWidget(self.varStar_xPickLbl, 3, 1)
        starTableLayout.addWidget(self.varStar_yPickLbl, 3, 2)
        starTableLayout.addWidget(self.varStar_magLbl, 3, 3)
        starTableLayout.addWidget(self.varStar_pickBtn, 3, 4)
        starTableLayout.addWidget(self.varStar_imgLbl, 3, 5)
        self.varStar_pickBtn.clicked.connect(lambda: self.initStarImage(self.varStar, "Variable Star"))
        
        mainLayout.addWidget(starTableGroupBox)

        controlButtonsLayout = QHBoxLayout()
        self.selectImageBtn = QPushButton("Select Image")
        self.selectImageBtn.clicked.connect(self.selectImage) # Connect
        self.evalMagnitudeBtn = QPushButton("Evaluate")
        self.evalMagnitudeBtn.clicked.connect(self.evaluateMagnitude) # Connect 
        
        controlButtonsLayout.addWidget(self.selectImageBtn)
        controlButtonsLayout.addWidget(self.evalMagnitudeBtn)
        mainLayout.addLayout(controlButtonsLayout)

        self.imageScene = QGraphicsScene(self)
        self.imageDisplayView = QGraphicsView(self.imageScene)
        self.imageDisplayView.setMinimumSize(640, 480)
        self.imageDisplayView.setDragMode(QGraphicsView.ScrollHandDrag)
        self.imageDisplayView.setRenderHint(QPainter.Antialiasing)
        self.imageDisplayView.setRenderHint(QPainter.SmoothPixmapTransform)
        mainLayout.addWidget(self.imageDisplayView)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(self.filename)

    def _displayImageInMainView(self, qpixmap_to_display):
        self.imageScene.clear()
        if qpixmap_to_display:
            self.imageScene.addPixmap(qpixmap_to_display)
            self.imageDisplayView.fitInView(self.imageScene.sceneRect(), Qt.KeepAspectRatio)
        else:
            # Display placeholder text if no image
            placeholder_text = self.imageScene.addText("Image will be displayed here.")
            placeholder_text.setDefaultTextColor(Qt.gray)


    def _updateCrosshairs(self):
        if not self.baseQtImg: # Ensure base image is loaded
            return

        # Create a fresh pixmap from the base image to draw on
        self.qtImg = self.baseQtImg.copy() 
        painter = QPainter(self.qtImg)
        
        stars_to_draw = [self.star1, self.star2, self.varStar]
        for star in stars_to_draw:
            if star.xPick != "0" and star.yPick != "0": # Check if star has been picked
                try:
                    x = int(star.xPick)
                    y = int(star.yPick)
                    
                    pen = QPen(QColor(*star.colour)) # Use star's defined color
                    pen.setWidth(2) # Set pen width
                    painter.setPen(pen)
                    
                    # Draw crosshair lines
                    painter.drawLine(x, y - 10, x, y - 2)
                    painter.drawLine(x, y + 2, x, y + 10)
                    painter.drawLine(x - 10, y, x - 2, y)
                    painter.drawLine(x + 2, y, x + 10, y)
                except ValueError:
                    print(f"Warning: Could not parse coordinates for a star: x={star.xPick}, y={star.yPick}")
                    continue # Skip this star if coordinates are invalid
        
        painter.end()
        self._displayImageInMainView(self.qtImg)


    def selectImage(self):
        options = QFileDialog.Options()
        # Use TIF extension as well, as per benchmark file
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image File", "", 
                                                  "Images (*.png *.xpm *.jpg *.jpeg *.bmp *.gif *.tif *.tiff);;All Files (*)", 
                                                  options=options)
        if fileName:
            try:
                self.filename = fileName
                self.pilImg = Image.open(self.filename)
                
                # Convert PIL image to QImage then to QPixmap
                # Ensure correct format handling, especially for various image modes (L, RGB, RGBA)
                if self.pilImg.mode == "RGBA":
                    image_data = self.pilImg.convert("RGBA").tobytes("raw", "BGRA")
                    qImage = QImage(image_data, self.pilImg.width, self.pilImg.height, QImage.Format_ARGB32)
                elif self.pilImg.mode == "RGB":
                    image_data = self.pilImg.convert("RGB").tobytes("raw", "BGR")
                    qImage = QImage(image_data, self.pilImg.width, self.pilImg.height, QImage.Format_RGB888)
                else: # Grayscale or other, convert to RGB for consistency for QPixmap
                    self.pilImg = self.pilImg.convert("RGB")
                    image_data = self.pilImg.tobytes("raw", "BGR")
                    qImage = QImage(image_data, self.pilImg.width, self.pilImg.height, QImage.Format_RGB888)

                self.baseQtImg = QPixmap.fromImage(qImage)
                self.qtImg = self.baseQtImg.copy() # qtImg will have crosshairs, baseQtImg is clean

                # Grayscale processing for CEAAL.py
                img_gray_pil = ImageOps.grayscale(self.pilImg)
                img_gray_pil = img_gray_pil.point(threshold_star_img) # Apply threshold
                self.img_gray_array = np.transpose(np.asarray(img_gray_pil)) # As per original code

                self.statusBar.showMessage(f"Selected image: {self.filename}")
                self._displayImageInMainView(self.qtImg)
                self._updateCrosshairs() # In case stars were picked before image load

                # Reset star data related to previous image
                for star, x_lbl, y_lbl, img_lbl in [
                    (self.star1, self.star1_xPickLbl, self.star1_yPickLbl, self.star1_imgLbl),
                    (self.star2, self.star2_xPickLbl, self.star2_yPickLbl, self.star2_imgLbl),
                    (self.varStar, self.varStar_xPickLbl, self.varStar_yPickLbl, self.varStar_imgLbl)
                ]:
                    star.xPick = "0"
                    star.yPick = "0"
                    # star.magnitude is handled by user input or calculation
                    x_lbl.setText("0")
                    y_lbl.setText("0")
                    img_lbl.clear()
                    img_lbl.setText(f"{img_lbl.objectName()[:5]} Img") # Reset placeholder text

            except Exception as e:
                QMessageBox.critical(self, "Image Load Error", f"Could not load image file: {fileName}\nError: {e}")
                self.filename = "No image selected."
                self.pilImg = None
                self.qtImg = None
                self.baseQtImg = None
                self.img_gray_array = None
                self.statusBar.showMessage(self.filename)
                self._displayImageInMainView(None)


    def initStarImage(self, star, star_name_label):
        if not self.pilImg or not self.baseQtImg:
            QMessageBox.warning(self, "No Image", "Please select an image first.")
            return

        # Pass the clean base image pixmap to the dialog
        # Also pass the current star's name for the dialog title
        dialog = PickStarDialog(self, self.baseQtImg, star_name_label)
        if dialog.exec_() == QDialog.Accepted:
            star.xPick = str(dialog.picked_x)
            star.yPick = str(dialog.picked_y)

            # Update labels in main UI
            target_img_lbl = None
            if star == self.star1:
                self.star1_xPickLbl.setText(star.xPick)
                self.star1_yPickLbl.setText(star.yPick)
                target_img_lbl = self.star1_imgLbl
            elif star == self.star2:
                self.star2_xPickLbl.setText(star.xPick)
                self.star2_yPickLbl.setText(star.yPick)
                target_img_lbl = self.star2_imgLbl
            else: # varStar
                self.varStar_xPickLbl.setText(star.xPick)
                self.varStar_yPickLbl.setText(star.yPick)
                target_img_lbl = self.varStar_imgLbl
            
            if self.img_gray_array is not None and self.pilImg is not None:
                try:
                    # Ensure coordinates are within image bounds before calling evalStarBBox
                    if not (0 <= dialog.picked_x < self.pilImg.width and \
                            0 <= dialog.picked_y < self.pilImg.height):
                        QMessageBox.warning(self, "Coordinates Out of Bounds", 
                                            "Picked coordinates are outside the image dimensions.")
                        star.xPick = "0" # Reset if out of bounds
                        star.yPick = "0"
                        if star == self.star1: self.star1_xPickLbl.setText("0"); self.star1_yPickLbl.setText("0")
                        elif star == self.star2: self.star2_xPickLbl.setText("0"); self.star2_yPickLbl.setText("0")
                        else: self.varStar_xPickLbl.setText("0"); self.varStar_yPickLbl.setText("0")
                        if target_img_lbl: target_img_lbl.clear()
                        self._updateCrosshairs()
                        return

                    star.evalStarBBox(self.img_gray_array)
                    
                    if star.xMin is None or star.xMax is None or star.yMin is None or star.yMax is None :
                         raise ValueError("Bounding box coordinates are invalid after evalStarBBox.")
                    if star.xMin >= star.xMax or star.yMin >= star.yMax:
                        raise ValueError(f"Invalid bounding box: xMin={star.xMin}, xMax={star.xMax}, yMin={star.yMin}, yMax={star.yMax}")


                    cropped_pil_img = self.pilImg.crop((star.xMin, star.yMin, star.xMax, star.yMax))
                    
                    if cropped_pil_img.width == 0 or cropped_pil_img.height == 0:
                        raise ValueError("Cropped image has zero width or height.")

                    if cropped_pil_img.mode == "RGBA":
                        c_image_data = cropped_pil_img.convert("RGBA").tobytes("raw", "BGRA")
                        c_qImage = QImage(c_image_data, cropped_pil_img.width, cropped_pil_img.height, QImage.Format_ARGB32)
                    elif cropped_pil_img.mode == "RGB":
                        c_image_data = cropped_pil_img.convert("RGB").tobytes("raw", "BGR")
                        c_qImage = QImage(c_image_data, cropped_pil_img.width, cropped_pil_img.height, QImage.Format_RGB888)
                    else: 
                        cropped_pil_img = cropped_pil_img.convert("RGB")
                        c_image_data = cropped_pil_img.tobytes("raw", "BGR")
                        c_qImage = QImage(c_image_data, cropped_pil_img.width, cropped_pil_img.height, QImage.Format_RGB888)
                    
                    cropped_qpixmap = QPixmap.fromImage(c_qImage)
                    if target_img_lbl:
                        target_img_lbl.setPixmap(cropped_qpixmap.scaled(target_img_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                except Exception as e:
                    print(f"Error during star bounding box evaluation or cropping for {star_name_label}: {e}")
                    QMessageBox.warning(self, "Star Processing Error", f"Could not process star {star_name_label}.\nError: {e}\nPlease pick again or check image.")
                    if target_img_lbl: target_img_lbl.setText("Error")
                    # Optionally reset star pick values
                    star.xPick = "0"
                    star.yPick = "0"
                    if star == self.star1: self.star1_xPickLbl.setText("0"); self.star1_yPickLbl.setText("0")
                    elif star == self.star2: self.star2_xPickLbl.setText("0"); self.star2_yPickLbl.setText("0")
                    else: self.varStar_xPickLbl.setText("0"); self.varStar_yPickLbl.setText("0")


            self._updateCrosshairs()

    def _evaluateRelativeLuminance(self):
        # Check if stars have been picked
        if self.star1.xPick == "0" or self.star2.xPick == "0" or self.varStar.xPick == "0":
            QMessageBox.warning(self, "Star Not Picked", "Please pick all three stars (Comp star 1, Comp star 2, Variable star) before evaluating.")
            return

        if self.img_gray_array is None:
            QMessageBox.critical(self, "Error", "Grayscale image data is not available. Please load an image.")
            return

        try:
            # Ensure imgArray is populated by evalStarBBox (called in initStarImage)
            if self.star1.imgArray is None or self.star2.imgArray is None or self.varStar.imgArray is None:
                 QMessageBox.critical(self, "Star Data Error", "Star image data not processed. Please re-pick stars or check image.")
                 return

            star1RelLum = self.star1.getAverageRelativeLuminance()
            star2RelLum = self.star2.getAverageRelativeLuminance()
            varStarRelLum = self.varStar.getAverageRelativeLuminance()
        except Exception as e:
            QMessageBox.critical(self, "Luminance Calculation Error", f"Could not calculate relative luminance for one or more stars.\nError: {e}\nPlease ensure stars are picked correctly within valid image areas.")
            return

        try:
            star1Mag_text = self.star1_magEdit.text()
            star2Mag_text = self.star2_magEdit.text()
            if not star1Mag_text or not star2Mag_text:
                QMessageBox.warning(self, "Input Error", "Please enter magnitudes for both comparison stars.")
                return
            star1Mag = float(star1Mag_text)
            star2Mag = float(star2Mag_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Magnitudes for comparison stars must be valid numbers.")
            return

        denominator = star2RelLum - star1RelLum
        if abs(denominator) < 1e-9:  # Avoid division by zero or very small numbers
            QMessageBox.critical(self, "Calculation Error", 
                                 "Relative luminance of comparison stars is too similar. Cannot calculate magnitude.\n"
                                 "Please check star picks or input magnitudes.")
            return

        alpha = (star2Mag - star1Mag) / denominator
        varStarMag_calc = alpha * (varStarRelLum - star1RelLum) + star1Mag
        
        self.varStar.magnitude = "{:.2f}".format(varStarMag_calc)
        self.varStar_magLbl.setText(self.varStar.magnitude)
        QMessageBox.information(self, "Evaluation Complete", f"Variable star magnitude calculated: {self.varStar.magnitude}")


    def evaluateMagnitude(self):
        self._evaluateRelativeLuminance()
        
    def openAboutWindow(self):
        dialog = AboutDialog(self)
        dialog.exec_()

    def saveData(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Data File", "", 
                                                  "CSV Files (*.csv);;Text Files (*.txt);;All Files (*)", 
                                                  options=options)
        if fileName:
            try:
                with open(fileName, 'w') as f:
                    f.write(f"Image File: {self.filename}\n\n")
                    f.write("Star,xPick,yPick,Magnitude,RelativeLuminance\n")
                    
                    # Star 1
                    s1_mag = self.star1_magEdit.text()
                    s1_rlum = self.star1.getAverageRelativeLuminance() if self.star1.imgArray is not None else "N/A"
                    f.write(f"Comparison Star 1,{self.star1.xPick},{self.star1.yPick},{s1_mag},{s1_rlum}\n")
                    
                    # Star 2
                    s2_mag = self.star2_magEdit.text()
                    s2_rlum = self.star2.getAverageRelativeLuminance() if self.star2.imgArray is not None else "N/A"
                    f.write(f"Comparison Star 2,{self.star2.xPick},{self.star2.yPick},{s2_mag},{s2_rlum}\n")
                    
                    # Variable Star
                    vs_mag = self.varStar.magnitude # Calculated magnitude
                    vs_rlum = self.varStar.getAverageRelativeLuminance() if self.varStar.imgArray is not None else "N/A"
                    f.write(f"Variable Star,{self.varStar.xPick},{self.varStar.yPick},{vs_mag},{vs_rlum}\n")
                
                QMessageBox.information(self, "Save Data", f"Data saved successfully to {fileName}")
            except Exception as e:
                QMessageBox.critical(self, "Save Data Error", f"Could not save data to file.\nError: {e}")


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About CEVaS")
        
        layout = QVBoxLayout(self)
        
        # Logo
        logoLabel = QLabel(self)
        logoPixmap = QPixmap("./logo_ceaal_transp.png")
        if logoPixmap.isNull():
            print("Warning: Could not load logo_ceaal_transp.png")
            logoLabel.setText("CEVaS Logo (not found)")
        else:
            logoLabel.setPixmap(logoPixmap.scaledToHeight(100, Qt.SmoothTransformation))
        logoLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(logoLabel)
        
        # Title
        titleLabel = QLabel("CEVaS", self)
        font = titleLabel.font()
        font.setPointSize(16)
        font.setBold(True)
        titleLabel.setFont(font)
        titleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(titleLabel)
        
        # Description
        descLabel = QLabel("CEVas (CEAAL Variable Stars) is a tool to help amateur astronomers measure the magnitude of variable stars.", self)
        descLabel.setWordWrap(True)
        descLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(descLabel)
        
        layout.addSpacing(15)
        
        # Developed by
        devByLabel = QLabel("Developed by:", self)
        devByLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(devByLabel)
        
        helvioLink = QLabel('<a href="http://www.linkedin.com/in/hfcpeixoto">Hélvio Peixoto</a>', self)
        helvioLink.setOpenExternalLinks(True)
        helvioLink.setAlignment(Qt.AlignCenter)
        layout.addWidget(helvioLink)
        
        ceaalLink = QLabel('<a href="http://www.ceaal.org.br">CEAAL - Centro de Estudos Astronômicos de Alagoas</a>', self)
        ceaalLink.setOpenExternalLinks(True)
        ceaalLink.setAlignment(Qt.AlignCenter)
        layout.addWidget(ceaalLink)
        
        githubLink = QLabel('<a href="https://github.com/hfcpeixoto/CEVaS">CEVaS on GitHub</a>', self)
        githubLink.setOpenExternalLinks(True)
        githubLink.setAlignment(Qt.AlignCenter)
        layout.addWidget(githubLink)
        
        layout.addSpacing(15)
        
        # OK Button
        okButton = QPushButton("OK", self)
        okButton.clicked.connect(self.accept)
        layout.addWidget(okButton, 0, Qt.AlignCenter)
        
        self.setLayout(layout)
        self.setFixedSize(self.sizeHint())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Set app icon (optional, if you have an icon file like logo_ceaal_transp.png)
    # app_icon = QIcon("./logo_ceaal_transp.png")
    # if not app_icon.isNull():
    #     app.setWindowIcon(app_icon)
    # else:
    #     print("Warning: Could not load application icon.")
        
    mainWindow = VariableStarsApp()
    mainWindow.show()
    sys.exit(app.exec_())