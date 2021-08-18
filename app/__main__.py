from app.helpers import update_hashes
import sys

if __name__ == '__main__':
    if 'update_hashes' in sys.argv:
        update_hashes()