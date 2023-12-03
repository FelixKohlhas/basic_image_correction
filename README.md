# BaSiCPy Image Correction

## Overview
BaSiCPy Image Correction is a Python script based on the BaSiCPy package, designed for background and shading correction of optical microscopy images. The default configuration is designed to be used with images from an IN Cell Analyzer 2200/2000, but it can be easily adapted to work with the output of other devices too.

## Requirements
- Python 3.x
- Dependencies: `basicpy`, `scikit-image`, `pandas`, `numpy`, `matplotlib`, `pyyaml`

## Installation
Install the required dependencies using the following command:
```bash
pip install basicpy scikit-image pandas numpy matplotlib PyYAML
```

## Usage
```bash
python basic_image_correction.py [--config CONFIG_PATH] directory_path directory_path_out directory_path_flatfield [--batch_size BATCH_SIZE] [--workers WORKERS]
```

### Arguments
- `directory_path`: Path of input images.
- `directory_path_out`: Output path for corrected images.
- `directory_path_flatfield`: Output path for flatfield images.
- `--config CONFIG_PATH`: Path to the configuration file (default: 'config.yaml').
- `--batch_size BATCH_SIZE`: Batch size for image processing (default: 0, meaning all images at once).
- `--workers WORKERS`: Number of workers for image processing (default: 1).

## Configuration
The script supports a configuration file in YAML format. An example `config.yaml` file is provided. It can include parameters such as `regex`, `groupby`, `workers`, and `batch_size`.

The most important setting is the `regex` parameter. It should be a Regular Expression that matches the relevant properties from filenames into capture groups. The script will then use these properties to group the images. More information about this can be found in [REGEX.md](REGEX.md)

## Output
The corrected images and flatfield images are saved in the specified output directories.

## Example
```bash
python basic_image_correction.py --config my_config.yaml /path/to/input_images /path/to/output_images /path/to/flatfield_images --batch_size 10 --workers 4
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.