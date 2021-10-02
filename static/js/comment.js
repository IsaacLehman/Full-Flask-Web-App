// =============================================================================
// XHR WRAPPER
// FOR GET/POST ENDPOINTS THAT RETURN JSON
//  >> onload = function(<json data|data>)
//
//
//  Example GET: 
//      const jsonRequest = new HttpRequest("GET", "/endpoint/", null, (jsonData)=>{console.log(jsonData)}, (error)=>{console.log(error)})
//
//  Example POST: 
//      const jsonRequest = new HttpRequest("POST", "/endpoint/", {key:value}, (jsonData)=>{console.log(jsonData)}, (error)=>{console.log(error)})
//
// BY: Isaac Lehman
// =============================================================================
class HttpRequest {
    constructor(method, url, data, onload, error) {
        this.method = method;
        this.url = url;
        this.data = data;
        this.onload = onload;
        this.error = error;
        this.xhr = new XMLHttpRequest();

        this.init();
    }

    init() {
        //create XMLHttpRequest object
        this.xhr.open(this.method, this.url)

        if (this.method == "POST") {
            // set content-type header to JSON
            this.xhr.setRequestHeader("Content-Type", "application/json");

            // send JSON data to the remote server
            this.xhr.send(JSON.stringify(this.data));
        } else {
            //send the Http request
            this.xhr.send()
        }

        // set error/load functions
        this.xhr.onload = this.onload;

        this.xhr.onerror = this.onerror;
    }


    set setHeader(key_value) {
        // Set a request header
        this.xhr.setRequestHeader(key_value.key, key_value.value);
    }


    get downloadProgress() {
        // Track data download progress
        // >> in Bytes
        this.xhr.onprogress = function (e) {
            return {
                loaded: e.loaded,
                total: e.total
            }
        }
    }


    get uploadProgress() {
        // Track data upload progress
        // >> in Bytes
        this.xhr.upload.onprogress = function (e) {
            return {
                loaded: e.loaded,
                total: e.total
            }
        }
    }
}


// =============================================================================
// Comment object
// ---
// Ajax
//    onLoad(e)
//    onError(e)
//    addComment(body)
// Comments
//    comments[]
//    buildComment(id, username, date, body)
//    setupComments()
//    createComment(data)
//    getComments()
//    init()
//    
//
// =============================================================================
var COMMENT_JS = (function (COMMENT_JS) {
    /**
     * Doc Ready
     */
    document.addEventListener("DOMContentLoaded", function () {
        COMMENT_JS.Comments.init(); // Set up event listeners for the comments section
    });

    COMMENT_JS.Ajax = {
        onLoad: function (e) {
            data = JSON.parse(e.target.response);
            console.log(data, data.length)

            if (data && Array.isArray(data.data)) {
                data.data.forEach(element => {
                    console.log(element)
                    COMMENT_JS.Comments.createComment(element);
                });
            } else {
                COMMENT_JS.Comments.createComment(data);
            }
            
        },
        onError: function (e) {
            console.log("ERROR", e);
        },
        addComment: function (body) {
            var new_comment = new HttpRequest(
                "POST",
                "/api/v1/comment" + String(window.location.pathname),
                { body: body },
                COMMENT_JS.Ajax.onLoad,
                COMMENT_JS.Ajax.onError
            );
        },
        get_comments: function () {
            var all_comments = new HttpRequest(
                "GET",
                "/api/v1/comment" + String(window.location.pathname),
                null,
                COMMENT_JS.Ajax.onLoad,
                COMMENT_JS.Ajax.onError
            );
        }
    }

    COMMENT_JS.Comments = {
        // ARRAY TO HOLD COMMENTS
        comments: [],

        buildComment: function (id, username, date, body) {
            return {
                id: id,
                username: username,
                date: date,
                body: body
            }
        },


        setupComments: function () {
            // ==========================================================
            //     COMMENT ADD/REMOVE FUNCTIONS
            // ==========================================================
            function onAdd(data) {
                COMMENT_JS.Comments.createComment(data);
            }
            function onRemove(id) {
                document.getElementById(id).remove();
            }


            // ==========================================================
            //     ADD TO THE DEFAULT PUSH/POP FUNCTIONS FOR COMMENTS
            // ==========================================================
            COMMENT_JS.Comments.comments.push = function () {
                Array.prototype.push.apply(this, arguments);
                onAdd(...arguments);
            };
            COMMENT_JS.Comments.comments.pop = function () {
                Array.prototype.push.apply(this, arguments);
                onRemove(...arguments);
            };
        },


        createComment: function (data) {
            // create a new div element
            let outerDiv = document.createElement("div");
            outerDiv.id = data.id;
            outerDiv.classList.add('card');
            //outerDiv.classList.add('rounded');
            outerDiv.classList.add('mt-3');
            //outerDiv.classList.add('mb-2');
            outerDiv.classList.add('shadow');

            let innerDiv = document.createElement("div");
            innerDiv.classList.add('card-body');


            // create body
            let body = document.createElement("div");
            body.classList.add('card-text');
            body.innerHTML = `<p class="comment-body"><img class="profile-img" src="/static/img/user.svg"> ${data.body}</p>`;

            // create details
            let footer = document.createElement("div");
            footer.classList.add('card-footer');
            footer.classList.add('text-muted');
            var date = Date.parse(data.date);
            //console.log(date.toString(), date.toLocaleString('en-US'), date)
            footer.innerHTML = `<span class="comment-user">@${data.username}</span>  <small class="comment-date" style="float:right">${data.date}</small>`;

            // add the elements to the newly created div
            innerDiv.appendChild(body);

            outerDiv.appendChild(innerDiv);
            outerDiv.appendChild(footer);

            // add the newly created element and its content into the DOM
            // at the top of the comments
            let commentDiv = document.getElementById("comment-div");
            commentDiv.insertAdjacentElement("afterbegin", outerDiv);
        },

        getComments: function () {

        },


        init: function () {
            COMMENT_JS.Comments.setupComments();

            // COMMENT FORM SUBMIT FUNCTIONS
            document.getElementById('comment-form').addEventListener('submit', function (e) {
                // prevent the form submission
                e.preventDefault();
                var form = e.target;
                var body_element = form.querySelector("#comment-body");
                if (body_element) {
                    var body = body_element.value; // get the value 
                    body_element.value = ''; // clear the value
                    COMMENT_JS.Ajax.addComment(body);
                }
            });

            // GET PREVIOUS COMMENTS
            COMMENT_JS.Ajax.get_comments();

        }
    }


    return COMMENT_JS;
}(COMMENT_JS || {}));