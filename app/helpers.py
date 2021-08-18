from uuid import uuid4
from pathlib import Path
from sqlalchemy.exc import OperationalError
import hashlib


from app.config import CAPYBARA_PATH


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def generate_filename(filename):
    file_suffix = filename.split('.')[-1]
    return  '{}.{}'.format(str(uuid4()), file_suffix)


def update_hashes():
    path = Path(CAPYBARA_PATH)
    hashes = [
        md5(file) for file in path.iterdir()
        if file.is_file()
        and not file.name.endswith('.md5')
    ]
    hashes = list(set(hashes))
    hash_path = path / Path('hashes.md5')
    with open(hash_path, 'w') as hash_file:
        hash_file.write('\n'.join(hashes))