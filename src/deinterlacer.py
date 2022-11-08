import os
from multiprocessing import Pool
import cv2 as cv
import numpy as np
from metadata import Metadata
from decoder import pgm_to_rgb, path_pgm_to_rgb


def weave(img1, img2):
    new_shape = list(img1.shape)
    new_shape[0] *= 2
    res = np.empty(new_shape)
    res[::2] = img1
    res[1::2] = img2
    return res

def bob(img):
    new_shape = [img.shape[1], img.shape[0] * 2]
    return cv.resize(img, new_shape, interpolation=cv.INTER_CUBIC)

def get_half_img(img, i):
    if i % 2 == 0:
        return img[::2, ...]
    return img[1::2, ...]

def none_deinterlacer(img, i):
    return img

def bob_deinterlace(img, i):
    img = get_half_img(img, i)
    # Opencv takes width, height order for new size!
    new_shape = [img.shape[1], img.shape[0] * 2]
    img = cv.resize(img, new_shape, interpolation=cv.INTER_CUBIC)
    return img

def mse(a, b):
    return ((a - b) ** 2).mean()

def spatial_deinterlacer(img, nextImg, threshold=50.0, s=(8, 16)):
    img1, img2 = img[::2], img[1::2]
    nextImg1, nextImg2 = nextImg[::2], nextImg[1::2]
    res1, res2 = np.zeros_like(img), np.zeros_like(img)

    for y in range(0, img1.shape[0], s[0]):
        for x in range(0, img1.shape[1], s[1]):
            t0 = img1[y:y+s[0], x:x+s[1]]
            b0 = img2[y:y+s[0], x:x+s[1]]
            t1 = nextImg1[y:y+s[0], x:x+s[1]]
            b1 = nextImg2[y:y+s[0], x:x+s[1]]
            E = max(mse(t0, t1), mse(b0, b1))
            if E > threshold:  # Movement
                res_t, res_b = bob(t0), bob(b0)
            else:  # Static
                res_t = weave(t0, b0)
                res_b = res_t
            res1[y * 2:y * 2 + (s[0] * 2), x:x + s[1]] = res_t
            res2[y * 2:y * 2 + (s[0] * 2), x:x + s[1]] = res_b
    return res1, res2

def deinterlace(path: str, nextPath: str, metadata: Metadata, deinterlacer_mode: str, threshold: float):
    img = path_pgm_to_rgb(path, metadata)
    imgInfo = metadata[Metadata.get_file_name(path)]
    if imgInfo.isProgressive:
        return [img]

    if deinterlacer_mode == 'none':
        res = [img, img]
    elif deinterlacer_mode == 'bob':
        res = [bob_deinterlace(img, 0), bob_deinterlace(img, 1)]
    elif deinterlacer_mode == 'spatial':
        nextImg = path_pgm_to_rgb(nextPath, metadata)
        res = list(spatial_deinterlacer(img, nextImg, threshold))
    else:
        raise Exception(f'Invalid deinterlacer mode specified: {deinterlacer_mode}')

    if not imgInfo.isTopFieldFirst:
        res = [res[1], res[0]]
    if imgInfo.isRepeatFirstField:
        res.append(res[0])
    return res


def transform_file(args: tuple[str, str, str, Metadata, str, float, int, int]):
    path, nextPath, cacheFolder, metadata, deinterlacer_mode, threshold, i, maxI = args
    if i % 100 == 0:
        print(f'Handling {i}/{maxI}th image')

    imgs = deinterlace(path, nextPath, metadata, deinterlacer_mode, threshold)

    displayPaths = []
    for i, img in enumerate(imgs):
        newPath = os.path.join(cacheFolder, Metadata.get_file_name(path) + f'_{i}.ppm')
        cv.imwrite(newPath, cv.cvtColor(img, cv.COLOR_RGB2BGR))
        displayPaths.append(newPath)
    return displayPaths

def transform_files_fast(paths: list[str], metadata: Metadata, mode: str, cacheFolder: str, threshold: float,
                         /, nb_thread: int = 8):
    print(f"Converting {len(paths)} file to rgb (using {nb_thread} threads)")
    args = [(paths[i], paths[i+1], cacheFolder, metadata, mode, threshold, i, len(paths)) for i in range(len(paths)-1)]

    if nb_thread == 1:
        newFiles = [transform_file(arg) for arg in args]
    else:
        with Pool(nb_thread) as p:
            newFiles = p.map(transform_file, args)

    return [item for sublist in newFiles for item in sublist]
