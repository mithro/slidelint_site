"""
Module with views for slidelint site.
"""
from pyramid.view import view_config
from hurry.filesize import size

import logging
LOGGER = logging.getLogger(__name__)


@view_config(context='.models.Counter', renderer='templates/index.pt')
def main_view(context, _):
    """
    Main site page view. Renders main template with angularjs app.
    It returns to renderer only number of checked presentations
    """
    return {'count': context.count}


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


@view_config(route_name='upload', request_method='POST', renderer="json")
def upload_view(request):
    """
    upload view - adds new job to the queue
    """
    settings = request.registry.settings

    rule = request.POST.get('check_rule', None)
    validation_error = validate_rule(rule)
    if validation_error:
        request.response.status_code = 400
        return validation_error

    max_allowed_size = int(settings.get('max_allowed_size', 15000000))
    upload_file = request.POST.get('file', None)
    validation_error = validate_upload_file(upload_file, max_allowed_size)
    if validation_error:
        request.response.status_code = 400
        return validation_error

    jobs_manager = settings['jobs_manager']
    info = jobs_manager.add_new_job(upload_file.file, rule)
    request.response.status_code = info.pop('status_code')
    return info


@view_config(route_name='results', request_method='POST', renderer="json")
def results_view(request):
    """
    checks if uid is in results
    """
    uid = request.json_body.get('uid', None)
    jobs_manager = request.registry.settings['jobs_manager']
    LOGGER.debug(
        'looking for "%s" in "%s"' % (uid, jobs_manager.results.keys()))
    if uid in jobs_manager.results:
        rez = jobs_manager.results.pop(uid)
        LOGGER.debug("send results to client")
        request.response.status_code = rez.get('status_code', 500)
        result = rez.get('result', 'something goes really wild')
        icons = rez.get('icons', [])
        return {'result': result, 'icons': icons}
    request.response.status_code = 404
    return {'msg': 'job "%s" was not found in results' % uid}


@view_config(route_name='app_js', renderer='templates/app_js.pt')
def app_js(request):
    """
    pass to app.js some arguments, like file size or number
    of checked presentations
    """
    request.response.content_type = 'text/javascript'
    settings = request.registry.settings
    max_allowed_size = int(settings.get('max_allowed_size', 15000000))
    return {'max_allowed_size': max_allowed_size}
