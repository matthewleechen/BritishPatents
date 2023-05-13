import argparse
import cv2
import json
import numpy as np
from pycocotools import mask as maskUtils
from pycocotools.coco import COCO


def visualize(image_id, image_path, annotations_path):
    # Load the COCO API and the annotations for the image
    coco = COCO(annotations_path)
    annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))

    # Load the image using OpenCV
    image = cv2.imread(image_path)

    # Get the height and width of the image
    height, width, _ = image.shape

    # Create a copy of the image to use as the overlay
    overlay = image.copy()

    # Loop over each annotation and add the segmentation mask to the overlay
    for anno in annotations:
        # Convert the segmentation to an RLE format
        rle = maskUtils.frPyObjects(anno['segmentation'], height, width)

        # Decode the RLE to a binary mask
        decoded_mask = maskUtils.decode(rle)

        # Remove any extra dimensions from the mask
        decoded_mask = np.squeeze(decoded_mask, axis=2)

        # Add the mask to the overlay
        mask = np.zeros((height, width), dtype=np.uint8)
        mask += decoded_mask
        overlay[mask == 1] = (0, 255, 0)

    # Set the transparency level of the overlay
    alpha = 0.5

    # Combine the overlay and original image using alpha blending
    cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

    # Display the final masked image
    cv2.imshow('Masked Image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Visualize segmentation masks')
    parser.add_argument('--image-id', type=int, required=True, help='ID of the image to visualize')
    parser.add_argument('--image-path', type=str, required=True, help='Path to the image file')
    parser.add_argument('--annotations-path', type=str, required=True, help='Path to the COCO annotations file')
    args = parser.parse_args()

    # Call the visualization function with the provided arguments
    visualize(args.image_id, args.image_path, args.annotations_path)
