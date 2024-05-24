import argparse
import json
import cv2

parser = argparse.ArgumentParser(description='Visualize annotated bounding boxes')
parser.add_argument('image_path', type=str, help='path to the image file')
parser.add_argument('image_id', type=int, help='ID of the image to visualize')
parser.add_argument('annotations_path', type=str, help='path to the annotations file (in COCO format)')

args = parser.parse_args()

# Load the annotations from the COCO format file
with open(args.annotations_path, 'r') as f:
    data = json.load(f)

annotations = data['annotations']
image_ids = data['images']
categories = data['categories']

# Get the image information
for image_info in image_ids:
    if image_info['id'] == args.image_id:
        break

# Load the image
image = cv2.imread(args.image_path)

# Loop over each annotation and draw the bounding box
for anno in annotations:
    if anno['image_id'] == args.image_id:
        # Convert bounding box values to integers
        x, y, w, h = [int(val) for val in anno['bbox']]
        # Draw the bounding box on the image
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Display the image with bounding boxes
cv2.imshow('image with bounding boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

