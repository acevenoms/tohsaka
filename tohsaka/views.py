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


@view_config(route_name='api_thread', renderer='json')
def api_thread(request):
    board = request.matchdict['board']
    thread = request.matchdict['thread']
    return model.get_single_thread(board, thread)


@view_config(route_name='board', renderer='templates/board.jinja2')
def board_view(request):
    board = request.matchdict['board']
    title = 'Board :: ' + board
    return {'page_title': title, 'controller': 'BoardController', 'board': board, 'posts_source': 1}


@view_config(route_name='new_thread', renderer='json')
def new_thread(request):
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


@view_config(route_name='thread', renderer='templates/board.jinja2')
def thread_view(request):
    board = request.matchdict['board']
    thread = request.matchdict['thread']
    title = 'Thread :: ' + thread
    return {'page_title': title, 'controller': 'ThreadController', 'board': board, 'posts_source': thread}


@view_config(route_name='reply', renderer='json')
def reply(request):
    fileinfo = model.upload_file(request.POST['file'])
    postid = model.post(request.matchdict['thread'],
                        request.matchdict['board'],
                        request.POST['author'],
                        request.POST['email'],
                        sha256_crypt.encrypt(request.POST['password']),
                        request.POST['comment'],
                        fileinfo,
                        False)
    return postid
