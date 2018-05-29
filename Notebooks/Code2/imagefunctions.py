import numpy as np
import pickle
import scipy
from skimage import color
from skimage.filters.rank import entropy
import pandas as pd
from sklearn.ensemble import AdaBoostClassifier
import math
from skimage.filters import gabor, gaussian
from skimage.morphology import opening
from skimage.morphology import disk
import cv2

np.random.seed(1337)

def rgb2ii(img, alpha = 0.5):
        """Convert RGB image to illumination invariant image."""
        ii_image = (0.5 + np.log(img[:, :, 1] / float(255)) -
                    alpha * np.log(img[:, :, 2] / float(255)) -
                    (1 - alpha) * np.log(img[:, :, 0] / float(255)))

        return ii_image
        
def preprocess(img):
    height, width, *rest = img.shape
    # Convert to CIELAB colorspace
    lab_img = color.rgb2lab(img)
    feature_array = lab_img
    # Calculate illuminance invariant image
    ii_img = rgb2ii(img).reshape(width, height, 1)
    feature_array = np.concatenate((feature_array, ii_img), axis=2)
    # Calculate texture pattern
    for sigma in [1, math.sqrt(2), 2]:
    # for sigma in [2]:
        g = gaussian(lab_img[:,:,0], sigma)
        feature_array = np.concatenate((feature_array, g.reshape(width, height, 1)), axis=2)
    # Calculate entropy
    # for i in range(6):
        # theta = i / 6 * np.pi
        # filtered_img = gabor(lab_img[:,:,0], frequency=1/(2*np.pi), theta=theta)[0]
        # feature_array = np.concatenate((feature_array, filtered_img.reshape(width, height, 1)), axis=2)
    for ws in [3, 5, 9]:
    # for ws in [9]:
        entropy_img = entropy(lab_img[:,:,0] / 100, disk(ws)) # 100 = Max L value
        feature_array = np.concatenate((feature_array, entropy_img.reshape(width, height, 1)), axis=2)
    
    feature_array = feature_array.reshape(feature_array.shape[0] ** 2, feature_array.shape[2])
    
    # Fill nans
    features = pd.DataFrame(feature_array)
    features.replace([np.inf, -np.inf], np.nan, inplace=True)
    features.fillna(0, inplace=True)

    return features.as_matrix()

# def preprocess(img):
    # height, width, *rest = img.shape
    # # Convert to CIELAB colorspace
    # lab_img = color.rgb2lab(img)
    # feature_array = lab_img
    # entropy_img = entropy(lab_img[:,:,0] / 100, disk(9)) # 100 = Max L value
    # feature_array = np.concatenate((feature_array, entropy_img.reshape(width, height, 1)), axis=2)
    
    # feature_array = feature_array.reshape(feature_array.shape[0] ** 2, feature_array.shape[2])
    
    # # Fill nans
    # features = pd.DataFrame(feature_array)
    # features.replace([np.inf, -np.inf], np.nan, inplace=True)
    # features.fillna(0, inplace=True)

    # return features.as_matrix()
    
def filter(img, filter_size=3):
    return opening(img, disk(filter_size))
        
def threshold(img, threshold=0.5, mode=cv2.THRESH_BINARY):
    ret, thresh = cv2.threshold(img, threshold, 1, mode)
    return thresh