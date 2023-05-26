import os
import argparse

# define command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("input_dir", help="directory containing input files")
args = parser.parse_args()

# iterate over all files in the input directory
for filename in os.listdir(args.input_dir):
    if filename.endswith(".txt"):
        # construct the full path to the input file
        input_path = os.path.join(args.input_dir, filename)
        
        # read in the contents of the input file
        with open(input_path, 'r') as f:
            lines = f.read().split('---')

        # Replace all separators with line breaks
        lines = [line.strip() for line in lines]

        # Replace double line breaks with single line breaks
        while '\n\n' in lines:
            lines = [line.replace('\n\n', '\n') for line in lines]

        # Merge paragraphs
        output = ''
        for i in range(0, len(lines), 2):
            if i == len(lines) - 1:
                output += lines[i]
            else:
                output += lines[i].strip() + '\n' + lines[i+1].strip() + '\n\n'

        # overwrite the input file with the modified content
        with open(input_path, 'w') as f:
            f.write(output)
