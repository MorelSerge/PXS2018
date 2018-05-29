from geojsonimagefetcher import GeoJsonImageFetcher
from skimage.morphology import opening
from skimage.morphology import disk, square
import cv2
import json
import numpy as np

class TreeCalculator:
    
    def __init__(self, model):
        self.model = model
        
    def calculate_from_file(self, file, zoom=16, hq=True):
        json = json.load(open(file))
        return self.calculate_from_geojson(json, zoom, hq)
        
    def calculate_from_geojson(self, json, zoom=16, hq=True):
        fetcher = GeoJsonImageFetcher()
        return self.calculate_from_images(fetcher.fetch_sat_images(json, zoom, hq))
        
    def calculate_from_images(self, images, filter_size=3):
        coverages = []
        for image in images:
            predicted_image = self.model.predict_proba(image)
            coverages.append(self.calculate_tree_coverage(predicted_image, filter_size))
        return np.mean(coverages)
        
    def filter_image(self, img, filter_size=3):
        return opening(img, disk(filter_size))
        
    def threshold_image(self, img, threshold=0.5, mode=cv2.THRESH_BINARY):
        ret, thresh = cv2.threshold(img, threshold, 1, mode)
        return thresh
            
    def calculate_tree_coverage(self, prediction, filter_size=3):
        filtered_img = self.filter_image(prediction, filter_size)
        thresh = self.threshold_image(filtered_img)
        coverage = np.count_nonzero(thresh) / thresh.size
        return coverage