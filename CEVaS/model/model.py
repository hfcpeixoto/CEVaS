from CEVaS.model.star import Star

class Model:
    def __init__(self):
        self._selectedImageFrame = ""

        self.filename = "No image selected."
        self.img = ""
        self.selectedImageId = 0

        self.star1 = Star(colour=(255, 255, 0))
        self.star2 = Star(colour=(255, 0, 0))
        self.varStar = Star(colour=(255, 0, 255))
