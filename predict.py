# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# PDX-License-Identifier: MIT-0 (For details, see https://github.com/awsdocs/amazon-rekognition-custom-labels-developer-guide/blob/master/LICENSE-SAMPLECODE.)

import boto3
import io
from PIL import Image, ImageDraw, ExifTags, ImageColor, ImageFont


def display_image(bucket, photo, response):
    # Load image from S3 bucket
    s3_connection = boto3.resource("s3")

    s3_object = s3_connection.Object(bucket, photo)
    s3_response = s3_object.get()

    stream = io.BytesIO(s3_response["Body"].read())
    image = Image.open(stream)

    # Ready image to draw bounding boxes on it.
    imgWidth, imgHeight = image.size
    draw = ImageDraw.Draw(image)

    # calculate and display bounding boxes for each detected custom label
    print("Detected custom labels for " + photo)
    for customLabel in response["CustomLabels"]:
        print("Label " + str(customLabel["Name"]))
        print("Confidence " + str(customLabel["Confidence"]))
        if "Geometry" in customLabel:
            box = customLabel["Geometry"]["BoundingBox"]
            left = imgWidth * box["Left"]
            top = imgHeight * box["Top"]
            width = imgWidth * box["Width"]
            height = imgHeight * box["Height"]

            fnt = ImageFont.truetype("/Library/Fonts/Arial.ttf", 50)
            draw.text((left, top), customLabel["Name"], fill="#00d400", font=fnt)

            print("Left: " + "{0:.0f}".format(left))
            print("Top: " + "{0:.0f}".format(top))
            print("Label Width: " + "{0:.0f}".format(width))
            print("Label Height: " + "{0:.0f}".format(height))

            points = (
                (left, top),
                (left + width, top),
                (left + width, top + height),
                (left, top + height),
                (left, top),
            )
            draw.line(points, fill="#00d400", width=5)

    image.show()


def show_custom_labels(model, bucket, photo, min_confidence):
    client = boto3.client("rekognition")

    # Call DetectCustomLabels
    response = client.detect_custom_labels(
        Image={"S3Object": {"Bucket": bucket, "Name": photo}},
        MinConfidence=min_confidence,
        ProjectVersionArn=model,
    )

    # For object detection use case, uncomment below code to display image.
    display_image(bucket, photo, response)

    return len(response["CustomLabels"])


def main():
    bucket = ""
    photo = "MY_IMAGE_KEY"
    model = "arn:aws:rekognition:ap-northeast-1:885382727844:project/recognition_of_weilong/version/recognition_of_weilong.2023-08-27T19.41.07/1693190467505"
    min_confidence = 95

    label_count = show_custom_labels(model, bucket, photo, min_confidence)
    print("Custom labels detected: " + str(label_count))


if __name__ == "__main__":
    main()
