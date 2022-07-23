import exiftool, sys, re
from pathlib import Path
from PIL import Image
from datetime import datetime
from tqdm import tqdm


def parse_exif_date(date_str):
    match = re.search(r"(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)", date_str)
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


def init_target_dir(f, date, base_path):
    year_path = base_path.joinpath(str(date.year))
    if not year_path.exists():
        year_path.mkdir()
    month_path = year_path.joinpath("{:02}".format(date.month))
    if not month_path.exists():
        month_path.mkdir()
    day_path = month_path.joinpath("{:02}".format(date.day))
    if not day_path.exists():
        day_path.mkdir()
    return day_path
    

def move_file(f, target):
    if not target.exists():
        target.mkdir()
    new_f = target.joinpath(f.name)
    f.rename(new_f)


def run(src_dir=".", target_dir="."):
    extensions = [".jpg", ".jpeg", ".heic", ".mov"]
    files = list(Path(src_dir).iterdir())
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
        
        created_date = get_date(f)
        if not created_date:
            no_metadata.append(f.name)
        else:
            target = init_target_dir(f, created_date, Path(target_dir))
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
    if len(sys.argv) == 3:
        run(sys.argv[1], sys.argv[2])