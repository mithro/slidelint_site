"""
Module with views for slidelint site.
"""
from pyramid.view import view_config
from pyramid.renderers import render
from pyramid.response import Response
from .validators import validate_rule, validate_upload_file
from pyramid_mailer.message import Message
from pyramid_mailer import get_mailer
import transaction

import logging
LOGGER = logging.getLogger(__name__)


@view_config(route_name='feedback', request_method="POST", renderer='json')
def feedback(request):
    """
    Feedback view - send to site administrator user feedback message
    """
    mgs = request.json_body.get('message', None)
    uid = request.json_body.get('uid', '')
    if not mgs or uid:
        request.response.status_code = 400
        return {'error': 'you should provide message and job uid'}

    mailer = get_mailer(request)
    settings = request.registry.settings

    body = "Job id: %s\nFeedback text:\n%s" % (uid, mgs)

    message = Message(
        subject=settings['mail.subject'],
        sender=settings['mail.sender'],
        recipients=settings['mail.recipients'],
        body=body)
    mailer.send(message)
    transaction.commit()
    return {'status': 'ok'}


@view_config(context='.models.Counter')
def main_view(context, request):
    """
    Main site page view. Renders main template with angularjs app.
    It returns to renderer only number of checked presentations
    """
    if request.method == 'GET':
        return Response(
            render('templates/index.pt', {'count': context.count}, request))

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
    context.increment()
    return Response(render('json', info, request))


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


@view_config(
    name='app.js', context='.models.Counter', renderer='templates/app_js.pt')
def app_js(context, request):
    """
    pass to app.js some arguments, like file size or number
    of checked presentations
    """
    request.response.content_type = 'text/javascript'
    settings = request.registry.settings
    max_allowed_size = int(settings.get('max_allowed_size', 15000000))
    return {'max_allowed_size': max_allowed_size, 'count': context.count}
