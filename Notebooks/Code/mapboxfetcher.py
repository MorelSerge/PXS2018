import utils
import matplotlib.pyplot as plt
import numpy as np
from urllib import request
import PIL
import io

class  MapBoxFetcher:
    
    class MapBoxImageBytes:
        def __init__(self, image_bytes):
            self.image_bytes = image_bytes
            
        def image(self):
            return PIL.Image.open(io.BytesIO(self.image_bytes))
    
        def show(self):
            plt.imshow(np.asarray(self.image()))
            
        def bw(self):
            return self.image().convert('1')
        
        def bw_array(self):
            return np.asarray(self.bw())
            
        def array(self):
            return np.asarray(self.image())

        def save(self, path):
            with open(path, 'wb') as output:
                _ = output.write(self.image_bytes)
    
    def __init__(self, style_id='cjey0w5sw3a7i2sobc7ecztts'): # cjey0w5sw3a7i2sobc7ecztts = forest + tree crowns 3px; cjfuwjonm2r8p2sny75hyaegi = tree crowns 1px
        self.access_token = 'pk.eyJ1Ijoidmx1ZiIsImEiOiJjamVpbDMxamEwYmI3MnFuNW8ybnI0NHdyIn0.dxuL9WvARgL4FFbSt-KUqA'
        self.style_id = style_id
    
    def satellite(self, x, y, zoom, hq=False):
        # x, y = utils.deg2num(lat, lon, zoom)
        url = 'https://api.mapbox.com/v4/mapbox.satellite/{}/{}/{}{}.jpg70?access_token={}'.format(zoom, x, y, '' if not(hq) else '@2x', self.access_token)
        return self.MapBoxImageBytes(request.urlopen(url).read())
    
    def style(self, x, y, zoom, hq=False):
        # x, y = utils.deg2num(lat, lon, zoom)
        url = 'https://api.mapbox.com/styles/v1/vluf/{}/tiles/256/{}/{}/{}{}?access_token={}&fresh=true'.format(self.style_id, zoom, x, y, '' if not(hq) else '@2x', self.access_token)
        return self.MapBoxImageBytes(request.urlopen(url).read())