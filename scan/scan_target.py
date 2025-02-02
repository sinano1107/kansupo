from utils.rectangle import Rectangle


class ScanTarget:
    def __init__(self, rectangle: Rectangle, image: str, name: str = None):
        self.RECTANGLE = rectangle
        self.IMAGE = image
        self.NAME = name
    
    @property
    def name(self):
        if self.NAME is None:
            return self.RECTANGLE.NAME
        else:
            return self.NAME