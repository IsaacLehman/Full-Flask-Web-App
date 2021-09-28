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

function get_comments() {
    var onLoad = function (e) {
        data = JSON.parse(e.target.response);
        console.log(data);
    }
    var onError = function (e) {
        console.log("ERROR", e);
    }
    var all_comments = new HttpRequest(
        "GET", 
        "/api/v1/comment" + String(window.location.pathname), 
        null, 
        onLoad, 
        onError);
}

function get_new_comment_data() {
    return {
        body: 'This is a comment',
        parent_id: '345',
        reCAPTCHA: '123'
    }
}

function add_comment() {
    var onLoad = function (e) {
        data = JSON.parse(e.target.response);
        console.log(data);
    }
    var onError = function (e) {
        console.log("ERROR", e);
    }
    comment_data = get_new_comment_data();

    var new_comment = new HttpRequest(
        "POST", 
        "/api/v1/comment" + String(window.location.pathname), 
        comment_data, 
        onLoad, 
        onError);
} 

window.addEventListener('load', (event) => {
    add_comment();
    get_comments();
});
