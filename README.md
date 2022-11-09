# Video De-interlacing

Project for POGL and POGLA course at [EPITA](https://www.epita.fr/) made by
Dominique Michel et Lea Masselles

## What is it ?

This is a 2-person group project where we discover video interlacing and
implementing a small video player for interlaced videos.

The features are:
- Decode videos to frames and meta-data using a modified mpeg2dec
- Import image and metadata
- Store de-interlaced frames with custom algorithm :
    - none
    - bob
    - temporal
- Video playback with speed control (fps)

[TODO: video]


## Setup

### Tools
To be able to compile and run the program you need :
- C++ compiler of your choosing
- [SDL 1](https://www.libsdl.org/) (mpeg2dec dependency)
- [Python](https://python.org/) (language)
- [Pip](https://pypi.org/project/pip/) (python dependency manager)
    - numpy
    - opencv

### Installation

Install python requirements in a virtual environment :
```bash
42sh$ python -m venv env
42sh$ source env/bin/activate
(env) 42sh$ pip install -r requirements.txt
```

## Usage

### Flow presentation
1. Video extraction (frames and meta-data)
2. Video de-interlacing (custom methods)
3. Video playback

### Video extration

Video extraction is done using a supplied customized mpeg2dec. To avoid
handling the tool a simplification script has been created that will store all
files in "res/data".

```bash
42sh$ # ./script/gen.sh [FILE_NAME]
42sh$ ./script/gen.sh res/elementary/bw_numberes.m2v
```

### Video de-interlacing

Video de-interlacing can be executed using 3 methods:
    - none      (show frame raw)
    - bob       (resize and interpolate missing fields)
    - spatial   (mixing none and bob if "mouvement" in a given zone)

```bash
42sh$ # python src/main.py -m [META_DATA] -d [IMG_DIR] -D [METHOD] -t
[OUTPUT_TYPE] -c [CACHE_DIR_NAME] --max-frames [NUM_MAX_FRAMES]
42sh$ python src/main.py -m res/data/bw_numbers.cfg -d res/data/bw_numbers_imgs
-D bob -t ppm
```

### Video playback

Replay processed files with customisable speed (frame per seconds) :

```bash
42sh$ # python src/main.py -m [META_DATA] -T [PROCESSED_IMG_DIR] -t
[OUTPUT_TYPE] -s [SPEED_FPS]
42sh$ python src/main.py -m res/data/bw_numbers.cfg -T img_cache -t screen -s 2
```

## Known issues
- Code isnt a python module
- TODO

## Contributions
- Dominique MICHEL <dominique.michel@epita.fr>
- Léa MASSELLES <lea.masselles@epita.fr>
