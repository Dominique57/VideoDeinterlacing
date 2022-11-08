#!env/bin/python3
import argparse
import os
from metadata import Metadata
from display import display_video
from deinterlacer import transform_files_fast


def get_display_files(dirPath: str, metadata: Metadata, exts: list[str], maxFrame: int = None):
    files = []
    for i, imgInfo in enumerate(metadata):
        if maxFrame is not None and i >= maxFrame:
            break
        for ext in exts:
            imgPath = os.path.join(dirPath, imgInfo.name + ext)
            if os.path.exists(imgPath):
                files.append(imgPath)
            elif imgInfo.name == list(metadata.imageInfos.values())[-1].name:
                # Last may be missing due to mpeg2dec creating metadata but not always the frame
                del metadata.imageInfos[imgInfo.name]
                return files
            else:
                raise Exception(f"Missing frame {imgPath} !")
    return files

def run():
    parser = argparse.ArgumentParser(description='TVID decoder')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', type=str,
                       help='directory name containing input files')
    group.add_argument('-T', '--transformed-dir', type=str,
                       help='directory of already transformed files')
    parser.add_argument('-m', '--metadata', type=Metadata, required=True,
                        help="images metadata file")

    parser.add_argument('-D', '--dmode', type=str, choices=['none', 'bob', 'spatial'], default='none',
                        help='name of the de-interlace mode to use (default: none)')
    parser.add_argument('-t', '--type', type=str, choices=['screen', 'ppm'], required=True,
                        help='type of output')
    parser.add_argument('-c', '--cache', type=str, required=False, default='img_cache',
                        help='cache directory name to store transformed files (default: img_cache)')
    parser.add_argument('-s', '--speed', type=float, required=False,
                        help='overrides speed of generated video sequence in fps')
    parser.add_argument('--threshold', type=float, required=False, default=50,
                        help='in case of spatial deinterlacer, specifies threshold of movement (default: 50)')
    parser.add_argument('--no-heuristic', required=False, action='store_true',
                        help='disables heuristic check in case sequence_progressive is misused')
    parser.add_argument('--max-frames', type=int, required=False,
                        help='maximum number of frames to handle')

    args = parser.parse_args()
    args = vars(args)
    if not args['no_heuristic']:
        args['metadata'].applyHeuristics()
    if args['speed'] is not None:
        args['metadata'].seqInfo.fps = args['speed']

    # Get files in order
    files = []
    if args['transformed_dir']:
        if args['dmode'] != 'none':
            print('[WARN]: deinterlace mode ignored, loading images for display only !')
        files = get_display_files(args['transformed_dir'], args['metadata'], ['_0.ppm', '_1.ppm'], args['max_frames'])
    else:
        if not os.path.isdir(args['cache']):
            os.makedirs(args['cache'])
        if args['directory']:
            files = get_display_files(args['directory'], args['metadata'], ['.pgm'], args['max_frames'])
        files = transform_files_fast(files, args['metadata'], args['dmode'], args['cache'], args['threshold'])
        print(f'[INFO]: files saved in {args["cache"]} folder !')

    # Show files
    if args['type'] == 'screen':
        display_video(files, args['metadata'])
    else:
        if args['transformed_dir'] is not None:
            print('[WARN]: Specify transformed-dir when mode is not display does nothing !')


if __name__ == '__main__':
    run()
