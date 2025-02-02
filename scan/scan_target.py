from utils.rectangle import Rectangle


class ScanTarget:
    def __init__(self, rectangle: Rectangle, image: str):
        self.RECTANGLE = rectangle
        self.IMAGE = image