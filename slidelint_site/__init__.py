"""
Main pyramid app
"""
from pyramid.config import Configurator
from pyramid_zodbconn import get_connection
from .queue_manager import JobsManager
from .models import appmaker


def root_factory(request):
    """
    Data-base root factory
    """
    conn = get_connection(request)
    return appmaker(conn.root())


def main(global_config, **settings):  # pylint: disable=W0613
    """
    This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=root_factory, settings=settings)
    jobs_manager = JobsManager(
        settings['collector_chanel'],
        settings['producer_chanel'],
        settings['storage_dir'])
    config.registry.settings['jobs_manager'] = jobs_manager

    config.add_route('upload', '/upload')
    config.add_route('results', '/results')
    config.add_route('app_js', '/app.js')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('/debug', settings['debug_storage'])
    config.scan()
    return config.make_wsgi_app()
