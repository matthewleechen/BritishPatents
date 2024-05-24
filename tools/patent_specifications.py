#### Randomly sample patent specifications 
import os
import random
import json

def get_all_txt(folder_path):
    """
    grab all text files
    """
    txt_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".txt"):
                txt_files.append(os.path.join(root, file))
    return txt_files

def sample_txt_files(txt_files, sample_size=1000, seed=42):
    """
    random sampling
    """
    random.seed(seed)
    return random.sample(txt_files, min(sample_size, len(txt_files)))

def read_file(file_path):
    """
    read each file, first with utf-8 and if fails, with ISO-8859-1 
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='ISO-8859-1') as file: # try different encoding
                return file.read()
        except UnicodeDecodeError:
            return None

def create_label_studio_json(txt_files):
    """
    construct label studio formatted json
    """
    data = []
    for file_path in txt_files:
        content = read_file(file_path)
        if content is not None:
            data.append({
                "data": {
                    "text": content
                }
            })
    return data


folder_path = './drive/gb_patents/data/txts'
output_path = './drive/gb_patents/patents_ner/random_sample_patents.json'
    
txt_files = get_all_txt(folder_path)

sampled_files = sample_txt_files(txt_files, sample_size=1000, seed=42)

label_studio_data = create_label_studio_json(sampled_files)

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(label_studio_data, f, ensure_ascii=False, indent=4)

save_to_json(label_studio_data, output_path)
