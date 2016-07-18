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

    this.Post = function(board, thread, draft) {
        var postUrl = "/" + board + "/";
        if(thread != null) {
            postUrl = postUrl + thread + "/";
        }
        var post = new FormData();
        for (var key in draft) {
            post.append(key, draft[key]);
        }
        var request = $http.post(postUrl, post, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
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
.service("UtilService", function() {
    this.translateTimestamp = function(ts) {
        var dt = new Date(ts);
        var days = [
            'Sun',
            'Mon',
            'Tue',
            'Wed',
            'Thu',
            'Fri',
            'Sat'
        ];
        var year = dt.getFullYear();
        var month = zeroPad(dt.getMonth() + 1); // Month is zero-based
        var day = zeroPad(dt.getDate());
        var dayofweek = days[dt.getDay()];
        var hour = zeroPad(dt.getHours());
        var minute = zeroPad(dt.getMinutes());
        var second = zeroPad(dt.getSeconds());

        return year+"-"+month+"-"+day+"("+dayofweek+") "+hour+":"+minute+":"+second;
    };

    this.formatFileInfo = function(info) {
        var exponent = logBase(1024, info.bytes);
        var size = info.bytes / Math.pow(1024,exponent);
        var magnitudes = [
            "B",
            "KiB",
            "MiB"
        ];

        return size.toFixed(2)+" "+magnitudes[exponent]+"  "+info.width+"x"+info.height;
    };

    function logBase(base, n) {
        return Math.floor(Math.log(n) / Math.log(base));
    }

    function zeroPad(n) {
        if(n < 10) {
            return "0"+n;
        }
        else {
            return n;
        }
    }

    this.preparePosts = function(posts) {
        for (var t = 0; t < posts.threads.length; ++t) {
            posts.threads[t].expandImage = false;
            posts.threads[t].hoverPreview = false;
            if(posts.threads[t].author == '') {
                posts.threads[t].author = 'Anonymous'
            }
        }
        for (var thread in posts.replies) {
            for(var r = 0; r < posts.replies[thread].length; ++r) {
                posts.replies[thread][r].expandImage = false;
                posts.replies[thread][r].hoverPreview = false;
                if(posts.replies[thread][r].author == '') {
                    posts.replies[thread][r].author = 'Anonymous'
                }
            }
        }
        return posts;
    };
})
.controller("BoardController", function($scope, PostsService, UtilService) {
    $scope.posts = [];
    $scope.draft = {
        author: "",
        email: "",
        password: "",
        comment: "",
        file: {name: "Choose file..."}
    };
    $scope.currentBoard = 'b';
    $scope.currentPage = 1;
    $scope.showHideExpand = true;

    // Called in the page template, only useful until I have the ngRoute stuff setup
    $scope.init = function(board, page) {
        if(page == "") {
            page = $scope.currentPage;
        }
        else {
            $scope.currentPage = page;
        }
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

    $scope.setFiles = function(files) {
        $scope.draft.file = files[0];
        // Because we're outside of the binding system, we need to manually update the bindings
        $scope.$apply();
    };

    $scope.doPost = function() {
        if($scope.draft.file.name == "Choose file...") {
            // Clear out the file if it's just a placeholder
            $scope.draft.file = null;
        }
        PostsService.Post($scope.currentBoard, null, $scope.draft).then(postComplete);
    };

    $scope.util = UtilService;

    function loadPosts(posts) {
        $scope.posts = UtilService.preparePosts(posts.data);
    }

    function postComplete(result) {
        $scope.currentBoard = result.data.board;
        $scope.currentThread = result.data.thread;
        $scope.loadBoard(null, null);
        $scope.draft = {
            author: "",
            email: "",
            password: "",
            comment: "",
            file: {name: "Choose file..."}
        };
    }
})
.controller('ThreadController', function($scope, PostsService, UtilService) {
    $scope.posts = [];
    $scope.draft = {
        author: "",
        email: "",
        password: "",
        comment: "",
        file: {name: "Choose file..."}
    };
    $scope.currentBoard = 'b';
    $scope.currentThread = null;
    $scope.showHideExpand = false;

    // Called in the page template, only useful until I have the ngRoute stuff setup
    $scope.init = function(board, thread) {
        $scope.loadThread(board, thread)
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

    $scope.setFiles = function(files) {
        $scope.draft.file = files[0];
        // Because we're outside of the binding system, we need to manually update the bindings
        $scope.$apply();
    };

    $scope.doPost = function() {
        if($scope.draft.file.name == "Choose file...") {
            // Clear out the file if it's just a placeholder
            $scope.draft.file = null;
        }
        PostsService.Post($scope.currentBoard, $scope.currentThread, $scope.draft).then(postComplete);
    };

    $scope.util = UtilService;

    function loadPosts(posts) {
        $scope.posts = UtilService.preparePosts(posts.data);
    }

    function postComplete(result) {
        $scope.currentBoard = result.data.board;
        $scope.currentThread = result.data.thread;
        $scope.loadThread(null, null);
        $scope.draft = {
            author: "",
            email: "",
            password: "",
            comment: "",
            file: {name: "Choose file..."}
        };
    }
});