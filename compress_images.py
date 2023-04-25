import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

def compress(image_file):
    """
    Compresses a JPG image using JPEG format and saves it with the same file name.
    Overwrites the original file with the compressed version.

    Args:
        image_file (str): The path to the JPG image file to be compressed.

    Returns:
        None: The function does not return any value, but instead modifies the image file in place.
    """
    filepath = os.path.join(os.getcwd(), image_file)

    image = Image.open(filepath)

    # Convert image to RGB mode
    image = image.convert("RGB") # optional: depends on your input image

    # Save compressed image with same file name
    compressed_filename = os.path.splitext(image_file)[0] + "_compressed.jpg"
    compressed_filepath = os.path.join(os.getcwd(), compressed_filename)
    image.save(compressed_filepath, "JPEG", optimize=True, quality=20)

    # Remove original file
    os.remove(filepath)

    # Rename compressed file to original file name
    os.rename(compressed_filepath, filepath)

def compress_all_files(directory):
    """
    Compresses all JPG images in a specified directory using multithreading.
    Overwrites the original images with the compressed versions.

    Args:
        directory (str): The path to the directory containing the images to be compressed.

    Returns:
        None: The function does not return any value, but instead modifies the image files in place.

    Raises:
        OSError: If the specified directory does not exist or cannot be accessed.
    """
    with ThreadPoolExecutor(max_workers=2) as executor:
        for filename in os.listdir(directory):
            if filename.endswith(".jpg"):
                executor.submit(compress, os.path.join(directory, filename))

# Call compress_all_files() function on target directory
target_directory = "/path/to/directory" # change directory here
compress_all_files(target_directory)