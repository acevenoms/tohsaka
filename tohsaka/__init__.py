from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('index', '/')
    config.add_route('board', '/{board}/', request_method='GET')
    config.add_route('newpost', '/{board}/', request_method='POST')
    config.add_route('thread', '/{board}/{thread}/', request_method='GET')
    config.add_route('reply', '/{board}/{thread}/', request_method='POST')
    config.scan()
    return config.make_wsgi_app()
