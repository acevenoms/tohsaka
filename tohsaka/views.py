from pyramid.view import view_config, notfound_view_config
from pyramid.httpexceptions import HTTPNotFound


@notfound_view_config(append_slash=True)
def notfound(request):
    return HTTPNotFound('')


@view_config(route_name='index', renderer='templates/index.jinja2')
def index_view(request):
    return {'page_title': 'index', 'project': 'index'}


@view_config(route_name='board', renderer='templates/index.jinja2')
def board_view(request):
    return {'page_title': 'board', 'project': 'board'}


@view_config(route_name='thread', renderer='templates/index.jinja2')
def thread_view(request):
    return {'page_title': 'thread', 'project': 'thread'}
