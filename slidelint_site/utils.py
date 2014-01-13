"""
Bunch of useful functions
"""
import os
import shutil
# import tempfile
# import base64
# import subprocess

import logging
LOGGER = logging.getLogger(__name__)


def save_file(file_object, uid, base_path):
    """
    reads data from file_object and saves it into
    base_path/uid/presentation.pdf file,
    returns full path to this file
    """
    destiantion_dir = os.path.join(base_path, uid)
    os.mkdir(destiantion_dir)
    destiantion_file = os.path.join(destiantion_dir, 'presentation.pdf')
    with open(destiantion_file, 'wb') as destiantion_file_obj:
        shutil.copyfileobj(file_object, destiantion_file_obj)
    LOGGER.debug('presentation file was saved to "%s"', destiantion_file)
    return destiantion_file

# def get_previews(path):
#     dist = path.rsplit(os.path.sep, 1)[0]
#     image_name = os.path.join(dist, 'preview-page')
#     cmd = ['pdftocairo', path, image_name, '-jpeg', '-scale-to', '300']
#     retcode = subprocess.call(cmd, timeout=600)
#     if retcode != 0:
#         raise IOError("Can't create presentation preview")
#     files = [i for i in os.listdir(dist) if i.startswith('preview-page')]
#     files.sort()
#     images = {'Slide %s' % (i+1): base64.b64encode(
#             open(os.path.join(dist, n), 'rb').read()).decode("utf-8")
#               for i, n in enumerate(files)}
#     return images
