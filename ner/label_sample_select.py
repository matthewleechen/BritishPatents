import os
import glob
import json
import random
import argparse

def main(folder_path, percent, seed):
    # get a list of all the .txt files in the folder
    file_list = glob.glob(os.path.join(folder_path, '*.txt'))

    # count the total number of patents across all the .txt files
    total_patents = 0
    for file_path in file_list:
        with open(file_path, 'r') as file:
            # read the file and split it into patents
            patents = file.read().split('\n\n')
            total_patents += len(patents)

    # set the random seed
    random.seed(seed)

    # select a percentage of the patents randomly
    num_selected_patents = int(total_patents * percent)
    selected_patents = random.sample(range(total_patents), int(total_patents*percent/100))

    # create a list to store the selected patents
    patents_list = []

    # loop over all the .txt files and append the selected patents to the list
    for file_path in file_list:
        with open(file_path, 'r') as file:
            # read the file and split it into patents
            patents = file.read().split('\n\n')

            # loop over the selected patents and append them to the list
            for i in selected_patents:
                if i < len(patents):
                    patents_list.append({
                        'file': file_path,
                        'text': patents[i]
                    })

    # save the selected patents to a .json file
    with open('selected_patents.json', 'w') as file:
        json.dump(patents_list, file)

    # print the total number of patents across all the .txt files
    print(f'Total number of patents: {total_patents}')
    print(f'Number of selected patents: {len(patents_list)} ({percent:.2f}% of all patents)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Select a random sample of patents from a folder of .txt files')
    parser.add_argument('folder_path', type=str, help='the path to the folder containing the .txt files')
    parser.add_argument('--percent', type=float, default=0.005,
                    help='percentage of patents to select (default: 0.5%)')
    parser.add_argument('--seed', type=int, default=42,
                    help='random seed (default: 42)')

    args = parser.parse_args()

    main(args.folder_path, args.percent, args.seed)


