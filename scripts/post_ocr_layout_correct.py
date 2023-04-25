import os

# Set the directory containing the text files
dir_path = "/path/to/folder/"

# Iterate over all .txt files in the directory
for filename in os.listdir(dir_path):
    if filename.endswith(".txt"):
        file_path = os.path.join(dir_path, filename)

        # Read the file contents
        with open(file_path, "r") as f:
            file_contents = f.read()

        # Replace "---\n---" with "---"
        modified_contents = file_contents.replace("---\n---", "---")

        # Remove leading and trailing spaces before and after separators
        modified_contents = modified_contents.replace(" \n---", "\n---").replace("---\n ", "---\n").replace("\n\n", "\n")

        # Write the modified contents back to the file
        with open(file_path, "w") as f:
            f.write(modified_contents)
