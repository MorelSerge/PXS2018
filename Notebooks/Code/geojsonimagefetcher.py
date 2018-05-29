import utils
from mapboxfetcher import MapBoxFetcher

class GeoJsonImageFetcher:

    def fetch_images(self, city, zoom=16, hq=True):
        city_polygon = utils.polygon_union(city['features'])
        city_bounds = city_polygon.bounds
        
        all_sat_imgs = []
        all_style_imgs = []
        
        fetcher = MapBoxFetcher()
        lat = city_bounds[3]
        lon = city_bounds[0]
        while lat >= city_bounds[1]:
            while lon <= city_bounds[2]:
                numx, numy = utils.deg2num(lat, lon, zoom)
                style_img = fetcher.style(lat, lon, zoom, hq=hq)
                sat_img = fetcher.satellite(lat, lon, zoom, hq=hq)
                
                all_sat_imgs.append(sat_img.array())
                all_style_imgs.append(style_img.bw_array())
                
                lon = utils.num2deg(utils.deg2num(lat, lon, zoom)[0] + 1, utils.deg2num(lat, lon, zoom)[1], zoom)[1]
            lon = city_bounds[0]
            lat = utils.num2deg(utils.deg2num(lat, lon, zoom)[0], utils.deg2num(lat, lon, zoom)[1] + 1, zoom)[0]
            
        return all_sat_imgs, all_style_imgs
    
    def fetch_sat_images(self, city, zoom=16, hq=True):
        city_polygon = utils.polygon_union(city['features'])
        city_bounds = city_polygon.bounds
        
        all_sat_imgs = []
        
        fetcher = MapBoxFetcher()
        lat = city_bounds[3]
        lon = city_bounds[0]
        while lat >= city_bounds[1]:
            while lon <= city_bounds[2]:
                numx, numy = utils.deg2num(lat, lon, zoom)
                sat_img = fetcher.satellite(lat, lon, zoom, hq=hq)
                
                all_sat_imgs.append(sat_img.array())
                
                lon = utils.num2deg(utils.deg2num(lat, lon, zoom)[0] + 1, utils.deg2num(lat, lon, zoom)[1], zoom)[1]
            lon = city_bounds[0]
            lat = utils.num2deg(utils.deg2num(lat, lon, zoom)[0], utils.deg2num(lat, lon, zoom)[1] + 1, zoom)[0]
        
        return all_sat_imgs
        
    def fetch_style_images(self, city, zoom=16, hq=True):
        city_polygon = utils.polygon_union(city['features'])
        city_bounds = city_polygon.bounds
        
        all_style_imgs = []
        
        fetcher = MapBoxFetcher()
        lat = city_bounds[3]
        lon = city_bounds[0]
        while lat >= city_bounds[1]:
            while lon <= city_bounds[2]:
                numx, numy = utils.deg2num(lat, lon, zoom)
                style_img = fetcher.style(lat, lon, zoom, hq=hq)
                
                all_style_imgs.append(style_img.bw_array())
                
                lon = utils.num2deg(utils.deg2num(lat, lon, zoom)[0] + 1, utils.deg2num(lat, lon, zoom)[1], zoom)[1]
            lon = city_bounds[0]
            lat = utils.num2deg(utils.deg2num(lat, lon, zoom)[0], utils.deg2num(lat, lon, zoom)[1] + 1, zoom)[0]
        
        return all_style_imgs