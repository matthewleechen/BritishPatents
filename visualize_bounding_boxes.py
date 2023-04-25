import json
import cv2

# Load the annotations from the result.json file (COCO format)
with open('result.json', 'r') as f:
    data = json.load(f)

annotations = data['annotations']
image_ids = data['images']
categories = data['categories']

# Get the image information
image_info = image_ids[0] # Change image_id: default 0
image = cv2.imread('/path/to/image') # File path to image with corresponding image_id

# Loop over each annotation and draw the bounding box
for anno in annotations:
    if anno['image_id'] == image_info['id']:
        # Convert bounding box values to integers
        x, y, w, h = [int(val) for val in anno['bbox']]
        # Draw the bounding box on the image
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

# Display the image with bounding boxes
cv2.imshow('image with bounding boxes', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
