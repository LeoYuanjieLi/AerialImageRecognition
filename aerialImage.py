# aerialImage.py
from typing import List

import boto3
import cv2
import numpy as np
from PIL import Image

from box import Box
from helpers import timing


class AerialImage:
    def __init__(self, s3_bucket: str, key: str, region_name="ap-northeast-1"):
        self.s3_bucket = s3_bucket
        self.key = key
        self.region_name = region_name
        self.loaded_aerial_image_array = None
        self.labels: List[Box] = []

    @timing
    def load_aerial_image(self):
        s3 = boto3.resource("s3", self.region_name)
        bucket = s3.Bucket(self.s3_bucket)
        file_stream = bucket.Object(self.key).get()[["Body"]]
        img = Image.open(file_stream)
        self.loaded_aerial_image_array = np.array(img)

    @staticmethod
    def write_image_to_s3(img_array, bucket, key, region_name, decode_format=".tif"):
        """Write an image array into S3 bucket

        Parameters
        ----------
        img_array: np.ndarray
        bucket: string
            Bucket name
        key: string
            Path in s3
        region_name: string
        decode_format: string
        Returns
        -------
        None
        """
        s3 = boto3.resource("s3", region_name)
        bucket = s3.Bucket(bucket)
        img_string = cv2.imencode(decode_format, img_array)[1].tobytes()
        img_object = bucket.Object(key)
        img_object.put(Body=img_string)

    @timing
    def scan_aerial_image(self, scan_size: int):
        pass

    @staticmethod
    def iou_algorithm(box1: Box, box2: Box):
        """We assume that the box follows the format:
        box1 = [x1,y1,x2,y2], and box2 = [x3,y3,x4,y4],
        where (x1,y1) and (x3,y3) represent the top left coordinate,
        and (x2,y2) and (x4,y4) represent the bottom right coordinate"""
        x1, y1, x2, y2 = box1.x1, box1.y1, box1.x2, box1.y1
        x3, y3, x4, y4 = box2.x1, box2.y1, box2.x2, box2.y1
        x_inter1 = max(x1, x3)
        y_inter1 = max(y1, y3)
        x_inter2 = min(x2, x4)
        y_inter2 = min(y2, y4)
        width_inter = abs(x_inter2 - x_inter1)
        height_inter = abs(y_inter2 - y_inter1)
        area_inter = width_inter * height_inter
        width_box1 = abs(x2 - x1)
        height_box1 = abs(y2 - y1)
        width_box2 = abs(x4 - x3)
        height_box2 = abs(y4 - y3)
        area_box1 = width_box1 * height_box1
        area_box2 = width_box2 * height_box2
        area_union = area_box1 + area_box2 - area_inter
        return area_inter / area_union

    @timing
    @staticmethod
    def deduplicate(box, search_range: int):
        """

        Parameters
        ----------
        box : list
        search_range: int representing pixel of the search area

        Returns
        -------
        """

