import numpy as np
import sko
from sko.GA import GA

class SalienceBKG():
    def __init__(self, img):
        self.img = img
        self.mask = None

    def ReshapeRGB(self):
        return self.img[:, :, :3] * np.expand_dims(self.img[:, :, 3], 2)

    def IdentifySalience(self):

class CropNScale():
    def __init__(self, img, resolution = [480,720]): # Aspect = Width,Height
        """

        :type img: numpy.array
        """
        self.img = img
        self.lefttop = (0,0)
        self.width = resolution[0]

    def OptimizeSC(self):


    def SalienceSC(self):
        

    def ShowIMG(self):
