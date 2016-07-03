angular.module("tohsaka", ["ngRoute"])
.service("PostsService", function($http, $q) {
    var errorMessage = null;

    this.GetPosts = function (board, page) {
        var request = $http({
            method: "GET",
            url: "/api/" + board + "/",
            params: {
                page: page
            }
        });

        return request.then(this.loadPosts, this.onError);
    };

    this.GetThread = function (board, thread) {
        var request = $http({
            method: "GET",
            url: "/api/" + board + "/" + thread + "/"
        });

        return request.then(this.loadPosts, this.onError);
    };

    this.Post = function(board, thread) {
        var postUrl = "/" + board + "/";
        if(thread != null) {
            postUrl = postUrl + thread + "/";
        }
        var request = $http({
            method: "POST",
            url: postUrl,
            data: draft
        });

        return request.then(this.onPost, this.onError)
    };

    this.loadPosts = function(response) {
        return response.data;
    };

    this.onPost = function(response) {
        return response.data;
    };

    this.onError = function(response) {
        errorMessage = response.message;
    };

    return {
        GetPosts: this.GetPosts,
        GetThread: this.GetThread,
        Post: this.Post,
        errorMessage: errorMessage
    };
})
.controller("PostController", function($scope, PostsService) {
    $scope.posts = [];
    $scope.draft = {};
    $scope.currentBoard = 'b';
    $scope.currentPage = 1;
    $scope.currentThread = null;

    // Called in the page template, only useful until I have the ngRoute stuff setup
    $scope.init = function(board, page, thread) {
        $scope.loadBoard(board, page)
    };

    $scope.loadBoard = function(board, page) {
        if(board != null && board != $scope.currentBoard) {
            $scope.currentBoard = board;
        }
        if(page >= 1 && page != $scope.currentPage) {
            $scope.currentPage = page;
        }
        // We get posts on a page regardless of if anything has changed in the controller,
        // because the remote model may have changed
        PostsService.GetPosts($scope.currentBoard, $scope.currentPage).then(loadPosts);
    };

    $scope.loadThread = function(board, thread) {
        if(board != null && board != $scope.currentBoard) {
            $scope.currentBoard = board;
        }
        if(thread != null && thread != $scope.currentThread)
        {
            $scope.currentThread = thread;
        }
        // We get posts on a page regardless of if anything has changed in the controller,
        // because the remote model may have changed
        PostsService.GetThread($scope.currentBoard, $scope.currentThread).then(loadPosts);
    };

    $scope.doPost = function() {
        PostsService.Post($scope.currentBoard, $scope.currentThread, $scope.draft).then(postComplete);
    };

    function loadPosts(posts) {
        $scope.posts = posts;
    }

    function postComplete(result) {
        $scope.currentBoard = result.board;
        $scope.currentThread = result.thread;
        $scope.loadThread(null, null);
        $scope.draft = {
            author: "",
            email: "",
            password: "",
            comment: "",
            file: null
        };
    }
});