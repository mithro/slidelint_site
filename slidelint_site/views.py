"""
Module with views for slidelint site.
"""
from pyramid.view import view_config

import logging
LOGGER = logging.getLogger(__name__)


@view_config(context='.models.Counter', renderer='templates/index.pt')
def main_view(context, _):
    """
    Main site page view. Renders main template with angularjs app.
    It returns to renderer only number of checked presentations
    """
    return {'count': context.count}


@view_config(route_name='upload', request_method='POST', renderer="json")
def upload_view(request):
    """
    upload view - adds new job to the queue
    """
    if 'check_rule' not in request.POST:
        return {'error': 'check_rule in not present in Post data'}
    if 'file' not in request.POST:
        return {'error': 'file in not present in Post data'}
    jobs_manager = request.registry.settings['jobs_manager']
    info = jobs_manager.add_new_job(
        request.POST['file'].file, request.POST['check_rule'])
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
