from pyramid.view import view_config, notfound_view_config
from pyramid.httpexceptions import HTTPNotFound
from passlib.hash import sha256_crypt

from tohsaka import model


@notfound_view_config(append_slash=True)
def notfound(request):
    return HTTPNotFound('')


@view_config(route_name='index', renderer='templates/index.jinja2')
def index_view(request):
    return {'page_title': 'index', 'project': 'index'}


@view_config(route_name='api_board', renderer='json')
def api_board(request):
    board = request.matchdict['board']
    page = request.params['page']
    return model.get_threads(board, page)


@view_config(route_name='board', renderer='templates/board.jinja2')
def board_view(request):
    board = request.matchdict['board']
    title = 'Board :: ' + board
    return {'page_title': title, 'board': board, 'page': 1, 'thread': 'null'}


@view_config(route_name='newpost', renderer='json')
def new_post(request):
    fileinfo = model.upload_file(request.POST['file'])
    postid = model.post(0,
                        request.matchdict['board'],
                        request.POST['author'],
                        request.POST['email'],
                        sha256_crypt.encrypt(request.POST['password']),
                        request.POST['comment'],
                        fileinfo,
                        False)
    return postid


@view_config(route_name='thread', renderer='templates/index.jinja2')
def thread_view(request):
    title = 'Thread :: ' + request.matchdict['thread']
    return {'page_title': title, 'project': 'thread'}


@view_config(route_name='reply', renderer='templates/index.jinja2')
def reply(request):
    title = 'Thread :: ' + request.matchdict['thread']
    return {'page_title': title, 'project': 'thread'}
