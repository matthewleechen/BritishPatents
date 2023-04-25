## Digitizing patent records
This repository contains the implementation for a deep learning pipeline to provide a clean digitization of the following records written by Bennett Woodcroft:
* Titles of Patents of Invention, Chronologically Arranged _(Mar 1617-Oct 1852)_ 
* Chronological Index of Patents Applied for and Patents Granted _(Oct 1852-Dec 1868)_
* Chronological and Descriptive Index of Patents Applied for and Patents Granted containing the Abridgements of Provisional and Complete Specifications _(Jan 1869-Dec 1871)_

The original page scans can be found across the [Internet Archive](https://archive.org/search?query=creator%3A%22Great+Britain.+Patent+Office%22), [Hathitrust](https://catalog.hathitrust.org/Record/101716274?type%5B%5D=all&lookfor%5B%5D=chronological%20index%20of%20patents&ft=ft) and [Google Books](https://www.google.com/search?hl=en&sxsrf=APwXEdeJNdCG7Aq1TS0ZjtwvOpmrV_635w:1682421539341&q=inauthor:%22Bennet+Woodcroft%22&tbm=bks). These also contained digitized text, but the layouts of these documents almost always result in poor quality OCR. This repository intends to provide an implementation that will yield sufficiently high quality OCR that can be used for downstream tasks such as named entity recognition and record linkage.

These records contain the universe of English patents issued between 1617 and 1852, and all British patents issued between 1852 and 1871. All records contain patent numbers and patentee information including full names, as well as location and occupational information. See below for example page scans of these records.

<img src="https://user-images.githubusercontent.com/63355658/234250327-8c07b174-b576-4bf0-bc21-93614f8904d6.jpg" width="250"> <img src="https://user-images.githubusercontent.com/63355658/234250202-1fb6fbff-b3a8-4a58-99c6-4feccdf64abb.jpg" width="264.5">  <img src="https://user-images.githubusercontent.com/63355658/234250176-6104f0ba-3fe4-4945-b3ee-a61e0b5e6bfe.jpg" width="263">

### Digitization Pipeline

The digitization pipeline consists of two stages: (1) fine tuning a layout detection model to predict bounding boxes around text; and (2) using Google Cloud Vision (GCV) to extract the text within the predicted bounding boxes. 

#### Annotations

All the annotations are available as a .json file [here](https://www.dropbox.com/s/o021e0a1t40181h/annotations_woodcroft_patents.json?dl=0), and as a COCO dataset [here](https://www.dropbox.com/s/gdpujktygeg79fm/annotations_woodcroft_patents.zip?dl=0). The original annotations can be edited and re-exported by importing the linked .json file into a [Label Studio](https://labelstud.io) project. The accompanying annotation schema is available [here](https://www.dropbox.com/s/bq9gqciksoxk6l8/annotation_schema.pdf?dl=0). The annotated bounding boxes can be visualized from the COCO dataset using the script [visualize_bounding_boxes.py](https://github.com/matthewleechen/digitize_woodcroft_patents/blob/main/tools/visualize_bounding_boxes.py).

For ease of annotation in Label Studio, the original images were compressed to 20% of their original quality using the script [compress_images.py](https://github.com/matthewleechen/digitize_woodcroft_patents/blob/main/tools/compress_images.py) (the quality parameter can be adjusted). To run this script, you need a single directory containing all the images you are looking to compress. 

In order to create a COCO dataset with segmentation masks, where the annotated masks are equivalent to the area enclosed by the annotated bounding box coordinates, you can run the script [create_seg_masks.py](https://github.com/matthewleechen/digitize_woodcroft_patents/blob/main/tools/create_seg_masks.py) using the linked COCO dataset. This will be necessary in order to train layout detection models that require segmentation masks (e.g. Mask-RCNN).

#### Fine Tuning


