import cv2
from pathlib import Path


def split_single_image(image_path: str, out_path: str):
    # Load the image
    img = cv2.imread(image_path)

    # Get the height and width of the image
    height = img.shape[0]
    width = img.shape[1]

    # Divide the image into four equal parts
    part1 = img[: height // 2, : width // 2]
    part2 = img[: height // 2, width // 2 :]
    part3 = img[height // 2 :, : width // 2]
    part4 = img[height // 2 :, width // 2 :]

    # Save each part of the image to a separate file
    cv2.imwrite(
        out_path + "/" + image_path.split("/")[-1].split(".")[0] + "_part1.png", part1
    )
    cv2.imwrite(
        out_path + "/" + image_path.split("/")[-1].split(".")[0] + "_part2.png", part2
    )
    cv2.imwrite(
        out_path + "/" + image_path.split("/")[-1].split(".")[0] + "_part3.png", part3
    )
    cv2.imwrite(
        out_path + "/" + image_path.split("/")[-1].split(".")[0] + "_part4.png", part4
    )


def split_images(in_directory, out_directory):
    from pathlib import Path

    path_list = Path(in_directory).glob("**/*.png")
    for path in path_list:
        split_single_image(str(path), out_directory)


if __name__ == "__main__":
    split_images("./assets_in", "./assets")
