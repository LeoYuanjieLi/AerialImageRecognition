# box.py
from numpy import int64


class Box:
    def __init__(self, x1: int64, y1: int64, x2: int64, y2: int64, confidence: float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.xc = (x1 + x2) // 2
        self.yc = (y1 + y2) // 2
        self.confidence = confidence
