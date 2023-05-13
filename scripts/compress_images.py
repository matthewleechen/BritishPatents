import os
import argparse
from PIL import Image


def compress(image_file, filetype, quality):
    """
    Compresses an image using JPEG format and saves it with the same file name.
    Overwrites the original file with the compressed version.

    Args:
        image_file (str): The path to the image file to be compressed.
        filetype (str): The type of the image file (e.g. 'jpg', 'png', 'jp2').
        quality (int): The quality of the compressed image, from 1 (worst) to 95 (best).

    Returns:
        None: The function does not return any value, but instead modifies the image file in place.
    """
    filepath = os.path.join(os.getcwd(), image_file)

    image = Image.open(filepath)

    # Convert image to RGB mode
    image = image.convert("RGB") # optional: depends on your input image

    # Save compressed image with same file name
    compressed_filename = os.path.splitext(image_file)[0] + "_compressed." + filetype
    compressed_filepath = os.path.join(os.getcwd(), compressed_filename)
    image.save(compressed_filepath, "JPEG", optimize=True, quality=quality)

    # Remove original file
    os.remove(filepath)

    # Rename compressed file to original file name
    os.rename(compressed_filepath, filepath)


def compress_all_files(directory, filetype, quality):
    """
    Compresses all images of a specified type in a directory.
    Overwrites the original images with the compressed versions.

    Args:
        directory (str): The path to the directory containing the images to be compressed.
        filetype (str): The type of the image files to be compressed (e.g. 'jpg', 'png', 'jp2').
        quality (int): The quality of the compressed image, from 1 (worst) to 95 (best).

    Returns:
        None: The function does not return any value, but instead modifies the image files in place.

    Raises:
        OSError: If the specified directory does not exist or cannot be accessed.
    """
    for filename in os.listdir(directory):
        if filename.endswith("." + filetype):
            compress(os.path.join(directory, filename), filetype, quality)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compress images in a directory')
    parser.add_argument('directory', type=str, help='path to the directory containing the images to be compressed')
    parser.add_argument('filetype', type=str, help='type of the image files to be compressed (e.g. jpg, png, jp2)')
    parser.add_argument('--quality', type=int, default=20, help='quality of the compressed image, from 1 (worst) to 95 (best)')

    args = parser.parse_args()

    # Call compress_all_files() function on target directory
    compress_all_files(args.directory, args.filetype, args.quality)


