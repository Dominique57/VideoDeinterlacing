import cv2 as cv
import numpy as np
import os
from actions import save_image
from multiprocessing import Pool
from metadata import Metadata

def cvt_yuv_to_rgb(yuv):
    yuv = yuv.astype(np.float32)
    yuv -= [16, 128, 128]
    factors = np.array([
        [1.164, 0, 1.596],
        [1.164, -0.392, -0.813],
        [1.164, 2.017,  0],
    ]).T
    rgb = np.rint(yuv.dot(factors))
    return np.clip(rgb, 0, 255).astype(np.uint8)


def resize_chroma_to_luma(chroma):
    new_shape = list(chroma.shape)
    new_shape[0] *= 2
    # group 2 by 2 lines, duplicate lines, degroup lines and duplicate cols
    return chroma.reshape(chroma.shape[0] // 2, chroma.shape[1] * 2)    \
        .repeat(2, 0)                                                   \
        .reshape((chroma.shape[0] * 2, chroma.shape[1]))                \
        .repeat(2, 1)

def pgm_to_rgb(img, imgInfo: Metadata.ImageInfo):
    # Extract separate fields
    row_luma = img.shape[0] * 2 // 3
    col_chroma = img.shape[1] // 2
    luma = img[:row_luma, ...]
    chroma_u = img[row_luma:, :col_chroma]
    chroma_v = img[row_luma:, col_chroma:]

    # Resample chroma to save size
    if imgInfo.isProgressive:
        chroma_u = chroma_u.repeat(2, 0).repeat(2, 1)
        chroma_v = chroma_v.repeat(2, 0).repeat(2, 1)
    else:
        chroma_u = resize_chroma_to_luma(chroma_u)
        chroma_v = resize_chroma_to_luma(chroma_v)

    # Merge yuv image together
    yuv = np.dstack([luma, chroma_u, chroma_v])
    rgb = cvt_yuv_to_rgb(yuv)
    return rgb

def path_pgm_to_rgb(path: str, metadata: Metadata):
    imgInfo = metadata[Metadata.get_file_name(path)]
    img = cv.imread(path, cv.IMREAD_UNCHANGED)
    return pgm_to_rgb(img, imgInfo)

def transform_file(arg):
    path, (i, cacheFolder, metadata, pathsLen) = arg
    fileNameExt = path.rsplit('/', 1)[1]
    fileName = fileNameExt.rsplit('.', 1)[0]
    img_pgm = cv.imread(path, cv.IMREAD_UNCHANGED)
    imgInfo = metadata[Metadata.get_file_name(path)]
    img_rgb = pgm_to_rgb(img_pgm, imgInfo)

    newPath = os.path.join(cacheFolder, fileName + '.ppm')
    save_image(img_rgb, newPath)
    print(f'{i + 1:2d}/{pathsLen} : Saved {path} to {newPath}')
    return newPath

def transform_files(paths: list[str], cacheFolder: str, metadata: Metadata, nb_thread=8):
    print(f"Converting {len(paths)} file to rgb (using {nb_thread} threads)")
    args = zip(paths, [(i, cacheFolder, metadata, len(paths)) for i in range(len(paths))])

    if nb_thread == 1:
        newFiles = [transform_file(arg) for arg in args]
    else:
        with Pool(nb_thread) as p:
            newFiles = p.map(transform_file, args)

    return newFiles
