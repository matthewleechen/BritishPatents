## Curating a dataset of British patents (1617-1871)
This repository contains the implementation for a deep learning pipeline to convert the following records written by Bennett Woodcroft into a structured dataset:
* Titles of Patents of Invention, Chronologically Arranged _(Mar 1617-Oct 1852)_ 
* Chronological Index of Patents Applied for and Patents Granted _(Oct 1852-Dec 1868)_
* Chronological and Descriptive Index of Patents Applied for and Patents Granted containing the Abridgements of Provisional and Complete Specifications _(Jan 1869-Dec 1871)_

The original page scans can be found across the [Internet Archive](https://archive.org/search?query=creator%3A%22Great+Britain.+Patent+Office%22), [Hathitrust](https://catalog.hathitrust.org/Record/101716274?type%5B%5D=all&lookfor%5B%5D=chronological%20index%20of%20patents&ft=ft) and [Google Books](https://www.google.com/search?hl=en&sxsrf=APwXEdeJNdCG7Aq1TS0ZjtwvOpmrV_635w:1682421539341&q=inauthor:%22Bennet+Woodcroft%22&tbm=bks). These also contained digitized text, but the layouts of these documents almost always result in poor quality OCR. This repository intends to provide an implementation that will yield sufficiently high quality OCR that can be used for downstream tasks such as named entity recognition and record linkage.

These records contain the universe of English patents issued between 1617 and 1852, and all British patents issued between 1853 and 1871. All records contain patent numbers and patentee information including full names, as well as location and occupational information. See below for example page scans of these records.

<img src="https://user-images.githubusercontent.com/63355658/234250327-8c07b174-b576-4bf0-bc21-93614f8904d6.jpg" width="250"> <img src="https://user-images.githubusercontent.com/63355658/234250202-1fb6fbff-b3a8-4a58-99c6-4feccdf64abb.jpg" width="264.5">  <img src="https://user-images.githubusercontent.com/63355658/234250176-6104f0ba-3fe4-4945-b3ee-a61e0b5e6bfe.jpg" width="263">

### Digitization Pipeline

The digitization pipeline consists of two stages: (1) fine tuning a layout detection model to predict bounding boxes around text; and (2) using Google Cloud Vision (GCV) to extract the text within the predicted bounding boxes. 

#### Annotations

All the annotations are available as a .json file [here](https://www.dropbox.com/s/o021e0a1t40181h/annotations_woodcroft_patents.json?dl=0), and as a COCO dataset [here](https://www.dropbox.com/s/gdpujktygeg79fm/annotations_woodcroft_patents.zip?dl=0). The original annotations can be edited and re-exported by importing the linked .json file into a [Label Studio](https://labelstud.io) project. The accompanying annotation schema is available [here](https://www.dropbox.com/s/bq9gqciksoxk6l8/annotation_schema.pdf?dl=0). The annotated bounding boxes can be visualized from the COCO dataset using the script [visualize_bounding_boxes.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/scripts/visualize_bounding_boxes.py). To run this script from the command line, assuming your COCO annotations are contained in the file ```result.json```, you can use

```
python visualize_bounding_boxes.py /path/to/image <image_id> /path/to/result.json
```

The images I select for manual labelling include all 1853 scans, and a sample of scans from 1617-1852, 1869, 1870 and 1871. Faster-RCNN and Mask-RCNN were both fine tuned on the full sample of annotations. I fine tuned Fast-RCNN only on the 1853 subsample, which is accessible as a COCO dataset [here](https://www.dropbox.com/s/idx7xe2ozl5hcj3/annotations_woodcroft_patents_1853.zip?dl=0).

For ease of annotation in Label Studio, the original images were compressed to 20% of their original quality using the script [compress_images.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/scripts/compress_images.py) (the ```<quality>``` parameter can be adjusted from 1-95\%, and the ```<filetype>``` parameter specifies the file format e.g. jpg, png, jp2). To run this script, you need a directory containing all the images you are looking to compress. Then you can use

```
python compress_images.py /path/to/directory <filetype> --quality <quality>
```

In order to create a COCO dataset with segmentation masks, where the annotated masks are equivalent to the area enclosed by the annotated bounding box coordinates, you can run the script [create_seg_masks.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/scripts/create_seg_masks.py) using the linked COCO dataset. This script will produce an output file ```new_results.json``` that contains segmentation masks. This will be necessary in order to train layout detection models that require segmentation masks (e.g. Mask-RCNN). To run this script, you can use

```
python create_seg_masks.py --annotations /path/to/result.json
```

The script to visualize the segmentation masks is [visualize_seg_masks.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/scripts/visualize_seg_masks.py). To run this script, you can use

```
python seg.py --image-id <image_id> --image-path /path/to/image --annotations-path /path/to/new_results.json
```

#### Fine Tuning Layout Detection Models

The Jupyter notebook for implementing fine tuning of the layout detection models is [fine_tuning.ipynb](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/notebooks/fine_tuning.ipynb). This notebook uses models from [Detectron2](https://github.com/facebookresearch/detectron2) and is based on scripts from [Layout Parser](https://github.com/Layout-Parser/layout-model-training).

#### Inference and GCV

This project uses GCV called from Layout Parser to digitize the text located within predicted bounding boxes. To get started with GCV, you are required to have a credentials file. To obtain a credentials file, you require a Google account. Instructions on setting up your credentials can be found [here](https://developers.google.com/workspace/guides/create-credentials). 

The notebook for running inference for layout detection and OCR to extract the text is [inference.ipynb](https://github.com/matthewleechen/woodcroft_patents/blob/main/layout_detection/notebooks/inference.ipynb). To run inference, you need a single directory containing all the images you are looking to digitize. I use a single directory for all the page scans for a given record book, and run inference through all the directories (books). You also need to upload the model configuration file and the weights from training. The notebook also allows you to visualize the layout model predictions on specific images.

### Named entity recognition

This section documents the fine tuning of a BERT model for named entity recognition (NER) on the digitized patents.

#### Data cleaning

The final outputs from inference using the digitization pipeline are .txt files containing a list of digitized bounding boxes with separators (---) between them. Because the text files are merged in page order, the bounding boxes require merging, i.e. the first and second boxes should be merged, as should the third and fourth, and so on. This stage will almost surely require manual checks to ensure that duplicate or erroneous text boxes are dropped. After manual checks, you can run the script [preprocess_ner.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/ner/scripts/preprocess_ner.py) to automate the box merging process. To run this script from the command line, assuming you have a directory containing all the .txt files, you can use

```
python preprocess_ner.py /path/to/directory
```

The merged text boxes that I use in this repository can be found [here](https://www.dropbox.com/s/0s2wjdeitufj8je/ocr_output.zip?dl=0). Because BERT has a token limit of 512, and the patents containing rich administrative information (1617-1852 Vol. 1) or complete specification information (1869-1871) can be extremely long, I have omitted the specification or administrative information for selected patents where the descriptions are particularly lengthy. This output can be cross-referenced with the original images and annotations, available [here](https://www.dropbox.com/s/o021e0a1t40181h/annotations_woodcroft_patents.json?dl=0). Each merged text box represents a single filed patent. Based on my own cross-referencing, the merged OCR output seems to be accurate.

#### Annotations

Annotations are made on a random sample of the patents. The script for randomly sampling a selected percentage (```<percent>```) of the patents and saving them to a .json file is [label_sample_select.py](https://github.com/matthewleechen/woodcroft_patents/blob/main/ner/scripts/label_sample_select.py). Note that the default percentage is 0.5% (```--percent 0.5```). This script generates a .json file, ```selected_patents.json``` when run. To run this, assuming you have a directory containing all the merged and cleaned .txt files, you can use

```
python label_sample_select.py /path/to/directory --percent <percent> --seed <random_seed>
```

This .json file is then uploaded to a Label Studio project task-by-task for labelling. The accompanying annotation schema is available [here](https://www.dropbox.com/s/z230vokn7627asy/ner_annotation_schema.pdf?dl=0). 

The annotations were made in a [Label Studio](https://labelstud.io) project. All the annotations are available as a .conll file [here](https://www.dropbox.com/s/k2tkl0ftlj1i26x/ner_patents.conll?dl=0) (and as a .json file [here](https://www.dropbox.com/s/jqmnaml3s16jha5/ner_patents.json?dl=0)). The original annotations can be edited and re-exported by importing the linked .json file into a Label Studio project.

#### Fine-tuning BERT

The notebook for fine-tuning BERT is [fine_tuning.ipynb](https://github.com/matthewleechen/woodcroft_patents/blob/main/ner/notebooks/fine_tuning.ipynb). This notebook is a slightly modified version of Niels Rogge's (extremely helpful!) notebook linked [here](https://github.com/NielsRogge/Transformers-Tutorials/blob/master/BERT/Custom_Named_Entity_Recognition_with_BERT.ipynb), and uses the Transformers library (HuggingFace site [here](https://huggingface.co/docs/transformers/index)). 

#### Inference

The notebook for running inference using the fine tuned model is [inference.ipynb](https://github.com/matthewleechen/woodcroft_patents/blob/main/ner/notebooks/inference.ipynb). This assumes that you have an input directory consisting of .txt files, and have an output directory that you want .csv files to exported to. The output is a .csv file containing the labelled classes as columns, and each patent being recorded as a row (observation).

#### Post-Processing

The inference process will result in a .csv file corresponding to each .txt file in the output directory. A Stata .do file that combines all .csv files and cleans the data is provided at [clean_ner_output.do](https://github.com/matthewleechen/woodcroft_patents/blob/main/ner/do_files/clean_ner_output.do). Errors can be manually cross-referenced against the raw image scans for accuracy.

