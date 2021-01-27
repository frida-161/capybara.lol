import os
from uuid import uuid4
from sqlalchemy.exc import OperationalError


def generate_filename(filename):
    file_suffix = filename.split('.')[-1]
    return  '{}.{}'.format(str(uuid4()), file_suffix)