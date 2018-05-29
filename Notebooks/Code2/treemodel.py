import numpy as np
import pickle
import scipy
from skimage import color
from skimage.filters.rank import entropy
from skimage.morphology import disk
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier
import math
import imagefunctions

np.random.seed(1337)

class TreeModel():

    def __init__(self, model):
        self.model = model # model should be trained
        
    def predict(self, img):
        height, width, *rest = img.shape
        return self.model.predict(imagefunctions.preprocess(img)).reshape(height, width)
        
    def predict_proba(self, img):
        height, width, *rest = img.shape
        return self.model.predict_proba(imagefunctions.preprocess(img))[:,1].reshape(height, width) # first column is probability of being tree
        
    def predict_np(self, img):
        height, width, *rest = img.shape
        return self.model.predict(img).reshape(height, width)
        
    def predict_proba_np(self, img):
        height, width, *rest = img.shape
        return self.model.predict_proba(img)[:,1].reshape(height, width) # first column is probability of being tree