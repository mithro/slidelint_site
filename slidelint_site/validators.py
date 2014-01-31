"""
Set of validators for views
"""
from hurry.filesize import size


def validate_rule(rule):
    """ Validator for checking rules """
    if rule not in ('simple', 'strict'):
        return {'error': 'check_rule in not present in Post data'}


def validate_upload_file(upload_file, max_allowed_size=15000000):
    """ Validator for file. Its checks file's type and size."""
    if upload_file is None:
        return {'error': 'file in not present in Post data'}
    fileobj = getattr(upload_file, 'file', None)
    if not fileobj:
        return {'error': 'file object is not present in posted data'}
    if not upload_file.filename.endswith('.pdf'):
        return {'error': 'file type is wrong - only PDF files are allowed'}
    if upload_file.type != 'application/pdf':
        return {'error': 'file type is not application/pdf'}

    # reading from file (uploading) a little bit more than is allowed
    fileobj.read(max_allowed_size+10)
    # getting cursor position (file size)
    file_size = fileobj.tell()
    fileobj.seek(0)
    if file_size > max_allowed_size:
        return {
            'error': 'File is too large, the max allowed file size to upload '
                     'is %s' % size(max_allowed_size)}
