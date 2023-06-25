import cv2 as cv

def draw_map(self, last_known):
    """Display basemap with scale, last know xy location, search areas."""

    cv.line(self.img, (20,370), (70,370), (0,0,0), 2)
    
