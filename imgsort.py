import exifread, pyheif, io, re, sys
from pathlib import Path
from datetime import datetime
from PIL import Image

def parse_exif_date(date_str):
    match = re.search("(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)", date_str)
    return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6)))


def get_date_from_heic(file_name):
    try:
        heif_file = pyheif.read_heif(file_name)

    except pyheif.error.HeifError as err:
        print(err)
        return None

    for metadata in heif_file.metadata:
        file_stream = io.BytesIO(metadata['data'][6:])
        tags = exifread.process_file(file_stream, details=False)
        date_str = str(tags.get("EXIF DateTimeOriginal"))
        match = re.search("(\d+):(\d+):(\d+) (\d+):(\d+):(\d+)", date_str)
        if match:
            return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), int(match.group(5)), int(match.group(6)))

def get_date_from_jpg(file_name):
    try:
        image = Image.open(file_name)
        exifdata = image._getexif()

        if exifdata:
            date_str = exifdata.get(36867)
            if (date_str):
                return parse_exif_date(date_str)

    except IOError as err:
        print(err)

def extension(file_name):
    match = re.search("\w+\.(\w+)", file_name)
    if match and match.group(1):
        return match.group(1)

def dir_name(date):
    return 

def get_target_name(f):
    date = get_date_from_jpg(f) if f.suffix.lower() == ".jpg" else get_date_from_heic(f)
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
    extensions = [".jpg", ".heic"]
    basepath = Path(base_path)
    files = basepath.iterdir()
    for f in files:
        print("Processing " + f.name)
        if not f.is_file():
            continue
        if not f.suffix.lower() in extensions:
            print("Unsupported file type: " + f.name)
            continue
        
        dir_name = get_target_name(f)
        if dir_name:
            target = basepath.joinpath(dir_name)
            move_file(f, target)

        #print(f.name + ": "  + dir_name + ": " + str(target.exists()))
        
            
if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) > 1:
        run(sys.argv[1])
    else:
        run()
