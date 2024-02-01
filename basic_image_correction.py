#!/usr/bin/env python

import re
import os
import pandas as pd
from basicpy import BaSiC
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
import argparse
import yaml

DEFAULT_CONFIG_PATH = 'config.yaml'
DEFAULT_BATCH_SIZE = 0
DEFAULT_WORKERS = 1

result_dtype = np.uint16
result_min = np.iinfo(result_dtype).min
result_max = np.iinfo(result_dtype).max

def parse_arguments():
    parser = argparse.ArgumentParser(description='BaSiC Image Correction Script')
    parser.add_argument('--config', default=DEFAULT_CONFIG_PATH, help='Path to config file')
    parser.add_argument('directory_path', help='Path of input images')
    parser.add_argument('directory_path_out', help='Output path for corrected images')
    parser.add_argument('directory_path_flatfield', help='Output path for flatfield images')
    parser.add_argument('--batch_size', type=int, default=DEFAULT_BATCH_SIZE, help='Batch size for image processing')
    parser.add_argument('--workers', type=int, default=DEFAULT_WORKERS, help='Number of workers for image processing')
    args = parser.parse_args()
    return args

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        config = yaml.safe_load(config_file) or {}
    return config

def load_images(directory_path, file_names):
    images = [io.imread(os.path.join(directory_path, file_name)) for file_name in file_names]
    return np.stack(images, axis=0)

def save_images(directory_path, file_names, images):
    for file_name, image in zip(file_names, images):
        file_path = os.path.join(directory_path, file_name)
        image = np.clip(image, result_min, result_max).astype(result_dtype)
        io.imsave(file_path, image, check_contrast=False)

def save_flatfield(directory_path_flatfield, name, flatfield, score):
    image_path_flatfield = os.path.join(directory_path_flatfield, f"{'_'.join(name)}.png")
    io.imsave(image_path_flatfield, (flatfield * 128).astype(np.uint8), check_contrast=False)
    return
    plt.figure()
    plt.imshow(flatfield, vmin=0.9, vmax=1.1)
    plt.colorbar()
    plt.title(f"Score: {score}")
    plt.tight_layout()
    plt.savefig(image_path_flatfield)
    plt.close()

def process_images_in_batches(images, batch_size, process_function):
    if batch_size == 0:
        batch_size = len(images)
    for i in range(0, len(images), batch_size):
        # print(f'Processing batch: {i} - {i + batch_size}')
        yield process_function(images[i:i + batch_size])

def main():
    args = parse_arguments()
    config = load_config(args.config)

    regex = config.get('regex', '')
    groupby = config.get('groupby', [])
    workers = args.workers or config.get('workers', DEFAULT_WORKERS)
    batch_size = args.batch_size or config.get('batch_size', DEFAULT_BATCH_SIZE)

    pattern = re.compile(regex)
    if not set(groupby).issubset(list(pattern.groupindex)):
        raise ValueError('Regex does not contain the same matching groups as the list of props to group by')

    os.makedirs(args.directory_path_out, exist_ok=True)
    os.makedirs(args.directory_path_flatfield, exist_ok=True)

    image_dicts = []

    for file_name in os.listdir(args.directory_path):
        match = re.search(pattern, file_name)
        if match:
            image_dict = match.groupdict()
            image_dict['_filename'] = file_name
            image_dict['_filepath'] = os.path.join(args.directory_path, file_name)
            image_dicts.append(image_dict)

    images = pd.DataFrame(image_dicts)
    images_grouped = images.groupby(groupby)
    
    print(f"{'_'.join(groupby)} (Number of images): Score")
    for name, group in images_grouped:
        print(f"{'_'.join(name)} ({len(group)})", end=': ', flush=True)

        file_names = list(group['_filename'])
        images = load_images(args.directory_path, file_names)

        basic = BaSiC()
        basic.max_workers = workers

        basic.fit(images)
        print(f'{basic.reweight_score:.4f}')

        process_function = lambda batch: basic.transform(batch)
        batches = process_images_in_batches(images, batch_size, process_function)

        for batch_result in batches:
            save_images(args.directory_path_out, file_names, batch_result)

        save_flatfield(args.directory_path_flatfield, name, basic.flatfield, basic.reweight_score)

if __name__ == "__main__":
    main()