from pathlib import Path
from PIL import Image
from datetime import datetime
from tqdm import tqdm

import exiftool, sys, re

def parse_exif_date(date_str):
    match = re.search("(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)", date_str)
    return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6)))

def get_date(f):
    tag_names = {'*': 'EXIF:DateTimeOriginal', '.mov': 'QuickTime:CreateDate'}
    tag = tag_names[f.suffix.lower()] if f.suffix.lower() in tag_names else tag_names['*']
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(str(f.absolute()))
        if not tag in metadata:
            return None
        date_str = metadata[tag]
        return parse_exif_date(date_str)

def get_target_name(f):
    date = get_date(f)
    if not date:
        #print("Could not extract date from " + f.name)
        return None
    return "{}-{:02}-{:02}".format(date.year, date.month, date.day)
    
def move_file(f, target):
    #print("Moving {} to {}".format(f.name, target.name))
    if not target.exists():
        target.mkdir()
    new_f = target.joinpath(f.name)
    f.rename(new_f)

def run(base_path = "."):
    extensions = [".jpg", ".heic", ".mov"]
    basepath = Path(base_path)
    files = list(basepath.iterdir())
    dirs = []
    unsupported = []
    no_metadata = []
    count = 0
    for f in tqdm(files, file=sys.stdout, desc="Processing files"):
        if not f.is_file():
            dirs.append(f.name)
            continue
        if not f.suffix.lower() in extensions:
            unsupported.append(f.suffix)
            continue
        
        dir_name = get_target_name(f)
        if not dir_name:
            no_metadata.append(f.name)
        else:
            target = basepath.joinpath(dir_name)
            move_file(f, target)
            count += 1
    print("Successfully processed {} files".format(count))
    if len(dirs) > 0:
        print("{} directories ignored".format(len(dirs)))
    if len(unsupported) > 0:
        print("{} files of unsupported file type ignored: {}".format(len(unsupported), set(unsupported)))
    if len(no_metadata) > 0:
        print("Could not extract metadata from {} files".format(len(no_metadata)))
        
            
if __name__ == "__main__":
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        run()