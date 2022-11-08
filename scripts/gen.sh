#!/bin/sh

# arg 1 (req.) : stream file to decode
# arg 2 (opt.) : mpeg additionnal arguments

# Parse arguments
[ "$#" -lt "1" ] && echo "Missing first argument: stream to decode" && exit 1
[ ! -e "$1" ] && echo "First argument: file not found" && exit 1
[ ! -f "$1" ] && echo "First argument must be a regular file" && exit 1
mpeg_args=""
if [ "$#" -ge "2" ]; then
  mpeg_args="-t $2"
fi

# Compute reference paths
video_path=$(readlink -f "$1")
script_dir=$(dirname "$(readlink -f "$0")")
root_dir=$(dirname "$script_dir")

# Define mpeg paths and check installation
mpeg_root_dir="$root_dir/third-party/mpeg2dec"
mpeg_bin="$mpeg_root_dir/src/mpeg2dec"
if [ ! -e "$mpeg_bin" ]; then
  cd "$mpeg_root_dir"                                                   \
    || { echo "cd failed, does '$mpeg_root_dir' exist ?" && exit 2; }
  { ./configure && make -j; }                           \
    || { echo "building mpeg2dec failed" && exit 2; }
  cd -                                      \
    || { echo "cd -: failed" && exit 2; }
fi

# Check project data directory
data_dir="$root_dir/res/data"
[ ! -e "$data_dir" ] && mkdir -p "$data_dir"

# Execute program
filename=$(filename="${video_path##*/}" && echo "${filename%.*}")
img_data_dir="$data_dir/${filename}_imgs"
[ ! -e "$img_data_dir" ]                                                    \
    && mkdir -p "$img_data_dir"                                             \
    && cd "$img_data_dir"                                                   \
    && echo "$mpeg_bin -o pgm $mpeg_args $video_path > ../$filename.cfg"    \
    && $mpeg_bin -o pgm $mpeg_args "$video_path" > "../$filename.cfg"
