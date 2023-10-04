# aerialImage.py
from typing import List

import boto3
import cv2
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = 20000000000
from box import Box
from helpers import timing


class AerialImage:
    def __init__(self, s3_bucket: str, key: str, region_name="ap-northeast-1"):
        self.s3_bucket = s3_bucket
        self.key = key
        self.region_name = region_name
        self.loaded_aerial_image_array = None
        self.labels: List[Box] = []
        self.scores: List[float] = []
        self.x_right_limit = 0
        self.y_bottom_limit = 0

    @timing
    def load_aerial_image(self):
        s3 = boto3.resource("s3", self.region_name)
        bucket = s3.Bucket(self.s3_bucket)
        file_stream = bucket.Object(self.key).get()[["Body"]]
        img = Image.open(file_stream)
        self.loaded_aerial_image_array = np.array(img)
        self.x_right_limit = self.loaded_aerial_image_arra.shape[0]
        self.y_bottom_limit = self.loaded_aerial_image_array.shape[1]

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

    @staticmethod
    def non_max_suppression(boxes, scores, threshold):
        """
        Perform non-maximum suppression on a list of bounding boxes given their scores.

        Args:
            boxes: List of bounding boxes in the format [x1, y1, x2, y2], where (x1, y1) and (x2, y2) are the
                   coordinates of the top-left and bottom-right corners.
            scores: List of confidence scores for each bounding box.
            threshold: IoU (Intersection over Union) threshold for suppressing overlapping boxes.

        Returns:
            List of indices to keep after non-maximum suppression.
        """
        if len(boxes) == 0:
            return []

        # Sort boxes by their scores in descending order
        sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        selected_indices = []
        while len(sorted_indices) > 0:
            current_index = sorted_indices[0]
            selected_indices.append(current_index)

            current_box = boxes[current_index]
            current_area = (current_box[2] - current_box[0] + 1) * (current_box[3] - current_box[1] + 1)

            for i in range(1, len(sorted_indices)):
                candidate_index = sorted_indices[i]
                candidate_box = boxes[candidate_index]
                intersection_x1 = max(current_box.x1, candidate_box.x1)
                intersection_y1 = max(current_box.y1, candidate_box.y1)
                intersection_x2 = min(current_box.x2, candidate_box.x2)
                intersection_y2 = min(current_box.y2, candidate_box.y2)
                intersection_area = max(0, intersection_x2 - intersection_x1 + 1) * max(0,
                                                                                        intersection_y2 - intersection_y1 + 1)

                iou = intersection_area / (current_area + (candidate_box[2] - candidate_box[0] + 1) * (
                            candidate_box[3] - candidate_box[1] + 1) - intersection_area)

                if iou > threshold:
                    sorted_indices.pop(i)
                else:
                    i += 1

        return selected_indices

    @timing
    def deduplicate(self, box, search_range: int):
        """

        Parameters
        ----------
        box : list
        search_range: int representing pixel of the search area

        Returns
        -------
        """
        boxes_within_range = self.search_boxes_from_point(box.xc, box.yc, search_range)
        if not boxes_within_range:
            return

        return self.non_max_suppression(boxes_within_range, self.scores, 0.75)




    @timing
    def search_boxes_from_point(self, x: int, y: int, search_range: int):
        """
        Naive method to search for boxes within given range
        Parameters
        ----------
        x
        y
        search_range

        Returns
        -------

        """
        x_left = max(0, x - search_range)
        x_right = min(x + search_range, self.x_right_limit)
        y_top = max(0, y - search_range)
        y_bottom = min(y + search_range, self.y_bottom_limit)
        result = []
        for box in self.labels:
            if x_left <= box.xc < x_right and y_top <= box.yc < y_bottom:
                result.append(box)

        return result
