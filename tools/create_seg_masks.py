# Dependency: pycocotools [requires Cython]

import json
from pycocotools.coco import COCO
import numpy as np
from pycocotools import mask as maskUtils
import cv2

# Load the annotations from the COCO result.json file
with open('result.json', 'r') as f:
    data = json.load(f)

annotations = data['annotations']
image_ids = data['images']
categories = data['categories']

# Create a COCO object and set its annotations and images attributes
coco = COCO()
coco.dataset['annotations'] = annotations
coco.dataset['images'] = image_ids
coco.dataset['categories'] = categories
coco.createIndex()

# Loop over each annotation and create a segmentation mask
for anno in annotations:
    # Extract the bounding box coordinates
    x, y, w, h = anno['bbox']
    # Create a segmentation mask from the bounding box coordinates
    anno['segmentation'] = [[x, y, x+w, y, x+w, y+h, x, y+h]]
    # Calculate the area of the bounding box
    anno['area'] = w * h

# Save the modified annotations to a new JSON file
with open('new_results.json', 'w') as f:
    json.dump(data, f)

### Optional: visualize segmentation masks for a selected image

# Get the ID of the first image in the dataset (change index for different image)
image_id = image_ids[0]['id'] 

# Load information about the image from the COCO API
image_info = coco.loadImgs(image_id)[0]

# Load the image that corresponds to the first image (id = 0) using OpenCV
image_path = '/path/to/image'
image = cv2.imread(image_path)

# Get the height and width of the image
height, width, _ = image.shape

# Load the annotations for the image from the COCO API
annotations = coco.loadAnns(coco.getAnnIds(imgIds=image_id))

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
