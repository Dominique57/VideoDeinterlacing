import cv2 as cv
import numpy as np
import time
from metadata import Metadata

def regroup_paths(paths: list[str], metadata: Metadata):
    res = []
    last_file_name = None
    for path in paths:
        file_name = Metadata.get_file_name(path).rsplit('_', 1)[0]
        if file_name == last_file_name:
            res[-1].append(path)
        else:
            res.append([path])
            last_file_name = file_name
    return res

def display_video(paths: list[str], metadata: Metadata):
    if len(paths) == 0:
        return

    paths_list = regroup_paths(paths, metadata)

    # Create window before drawing inside it
    cv.imshow('Video', np.zeros_like(cv.imread(paths[0])))
    frameWaitTime = 1.0 / metadata.seqInfo.fps
    i = 0
    while True:
        for path in paths_list[i]:
            start = time.time()
            img = cv.imread(path)
            cv.imshow('Video', img)
            wait_time = frameWaitTime / len(paths_list[i]) - (time.time() - start)

            if cv.waitKey(1) in [27]:
                return
            time.sleep(max(wait_time, 0))
        i = (i + 1) % len(paths_list)
