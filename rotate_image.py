import cv2


def rotate(image_path, out_path, angle, center=None, scale=1.0):
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(image, M, (w, h))

    cv2.imwrite(
        out_path
        + "/"
        + image_path.split("/")[-1].split(".")[0]
        + f"_rotated_{angle}.png",
        rotated,
    )


def rotate_image_in_directory(in_directory, out_directory):
    from pathlib import Path

    path_list = Path(in_directory).glob("**/*.png")
    for path in path_list:
        rotate(str(path), out_directory, 90)


if __name__ == "__main__":
    rotate_image_in_directory("training", "rotated_training")
