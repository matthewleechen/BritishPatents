import os

'''
Text files are in the format: chron_{year and vol/date info}_{page number}.txt (inherited from the format of the original image files).
You will likely need to amend the get_page_number function depending on the format of your original image files.

'''

# Define the directory path containing the text files
dir_path = '/path/to/folder'

# Get a list of the text files in the directory
files = [f for f in os.listdir(dir_path) if f.endswith('.txt')]

# Define a function to extract the page number from the file name
def get_page_number(file_name):
    return int(file_name.split('_')[-1].split('.')[0])

# Sort the files by page number
files = sorted(files, key=lambda f: get_page_number(f))

# Initialize the merged text as an empty string
merged_text = ""

# Iterate through each file
for file_name in files:
    # Open the file and read its contents
    with open(os.path.join(dir_path, file_name), 'r') as f:
        file_text = f.read().strip()
    # Add the file contents to the merged text, separated by ---
    merged_text += file_text + "\n---\n"

# Write the merged text to a new file
with open(os.path.join(dir_path, 'merged.txt'), 'w') as f:
    f.write(merged_text)
