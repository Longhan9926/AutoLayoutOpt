import numpy as np

class SalienceBKG():
    def __init__(self, img):
        self.img = img
        self.mask = None

    def ReshapeRGB(self):
        return self.img[:, :, :3] * np.expand_dims(self.img[:, :, 3], 2)

    def IdentifySalience(self):

class CropNScale():
    def __init__(self, img, aspect = [2,3]): # Aspect = Width,Height
        self.img = img
        self.lt = (0,0)
        self.width = aspect[0]

    def OptimizeSC(self):


    def SalienceSC(self):


    def ShowIMG(self):
