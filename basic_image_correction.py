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

def save_flatfield(directory_path_flatfield, name, flatfield, score):
    image_path_flatfield = os.path.join(directory_path_flatfield, f"{name}.png")
    io.imsave(image_path_flatfield, (flatfield * 128).astype(np.uint8), check_contrast=False)
    return
    plt.figure()
    plt.imshow(flatfield, vmin=0.9, vmax=1.1)
    plt.colorbar()
    plt.title(f"Score: {score}")
    plt.tight_layout()
    plt.savefig(image_path_flatfield)
    plt.close()

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
    
    for name, group in images_grouped:
        if isinstance(name, tuple):
            name = '_'.join(name)

        log_prefix = f"[{name}] "

        print(log_prefix + f"Number of images: {len(group)}")
        
        file_names = list(group['_filename'])

        basic = BaSiC()
        basic.max_workers = workers

        if batch_size == 0:
            batch_size = len(file_names)

        for i in range(0, len(file_names), batch_size):
            start = i
            end = min(i + batch_size, len(file_names))
            batch_file_names = file_names[start:end]
            print(log_prefix + f'Fitting batch: {start} - {end}', flush=True)

            images = []
            for file_name in batch_file_names:
                file_path = os.path.join(args.directory_path, file_name)
                images.append(io.imread(file_path))
            images = np.stack(images, axis=0)

            basic.fit(images)

        print(log_prefix + f'Score: {basic.reweight_score:.4f}', flush=True)

        for i in range(0, len(file_names), batch_size):
            start = i
            end = min(i + batch_size, len(file_names))
            batch_file_names = file_names[start:end]
            print(log_prefix + f'Transforming batch: {start} - {end}', flush=True)

            # If batch is whole dataset, no need to load images again
            if not batch_size == len(file_names):
                images = []
                for file_name in batch_file_names:
                    file_path = os.path.join(args.directory_path, file_name)
                    images.append(io.imread(file_path))
                images = np.stack(images, axis=0)

            batch_result = basic.transform(images)

            for file_name, image in zip(batch_file_names, batch_result):
                file_path = os.path.join(args.directory_path_out, file_name)
                image = np.clip(image, result_min, result_max).astype(result_dtype)
                io.imsave(file_path, image, check_contrast=False)

        save_flatfield(args.directory_path_flatfield, name, basic.flatfield, basic.reweight_score)

if __name__ == "__main__":
    main()
