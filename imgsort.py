from pathlib import Path
from PIL import Image
from datetime import datetime

import exiftool, sys, re

def parse_exif_date(date_str):
    match = re.search("(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)", date_str)
    return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6)))

def get_date(f):
    tag_names = {'*': 'EXIF:DateTimeOriginal', '.mov': 'QuickTime:CreateDate'}
    tag = tag_names[f.suffix.lower()] if f.suffix.lower() in tag_names else tag_names['*']
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(str(f.absolute()))
        date_str = metadata[tag]
        return parse_exif_date(date_str)

def get_target_name(f):
    date = get_date(f)
    if not date:
        print("Could not extract date from " + f.name)
        return None
    return "{}-{:02}-{:02}".format(date.year, date.month, date.day)
    
def move_file(f, target):
    print("Moving {} to {}".format(f.name, target.name))
    if not target.exists():
        target.mkdir()
    new_f = target.joinpath(f.name)
    f.rename(new_f)

def run(base_path = "."):
    extensions = [".jpg", ".heic", ".mov"]
    basepath = Path(base_path)
    files = basepath.iterdir()
    for f in files:
        print("Processing " + f.name)
        if not f.is_file():
            print("Ignoring directory " + f.name)
            continue
        if not f.suffix.lower() in extensions:
            print("Unsupported file type: " + f.name)
            continue
        
        dir_name = get_target_name(f)
        if dir_name:
            target = basepath.joinpath(dir_name)
            move_file(f, target)
        
            
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        run()