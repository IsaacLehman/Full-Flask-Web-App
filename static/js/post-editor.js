// FULL SCREEN
var elem = document.documentElement;
var full_screen = false;

function toggleFullScreen() {
    if (full_screen) {
        closeFullscreen();
        full_screen = false;
    } else {
        openFullscreen();
        full_screen = true;
    }
}

function openFullscreen() {
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msRequestFullscreen();
    }
}

function closeFullscreen() {
    if (document.exitFullscreen) {
        document.exitFullscreen();
    } else if (document.webkitExitFullscreen) { /* Safari */
        document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) { /* IE11 */
        document.msExitFullscreen();
    }
}

// Set options
// `highlight` example uses https://highlightjs.org
marked.setOptions({
    renderer: new marked.Renderer(),
    highlight: function (code, lang) {
        const language = hljs.getLanguage(lang) ? lang : 'plaintext';
        return hljs.highlight(code, { language }).value;
    },
    pedantic: false,
    gfm: true,
    breaks: false,
    sanitize: false,
    smartLists: true,
    smartypants: false,
    xhtml: false
});


// VARIABLES
var html = '';
var content = '';
var notes = '';
var is_edit_md = true;
var content_element = document.getElementById('content');
var process_element = document.getElementById('processed');
var processed_div = document.getElementById('processed-div');

// start marked up <If default value>
content = content_element.value;
html = marked(content);
process_element.innerHTML = html;




// ALLOW TABS
content_element.addEventListener('keydown', function (e) {
    if (e.key == 'Tab') {
        e.preventDefault();
        var start = this.selectionStart;
        var end = this.selectionEnd;

        // set textarea value to: text before caret + tab + text after caret
        this.value = this.value.substring(0, start) +
            "    " + this.value.substring(end);

        // put caret at right position again
        this.selectionEnd = start + 4;

        // Trigger input event to run md
        this.dispatchEvent(new Event('input'));
    }
});



/*
    localStorage.setItem('myCat', 'Tom');
    const cat = localStorage.getItem('myCat');
    localStorage.clear();
*/

// EVENT LISTENERS
content_element.addEventListener('input', (event) => {
    if (is_edit_md) {
        content = content_element.value;
        html = marked(content);
        process_element.innerHTML = html;
    } else {
        html = content_element.value;
        process_element.innerHTML = html;
    }

    if (process_element.innerHTML == '') {
        processed_div.classList.remove('thin-border');
    } else {
        processed_div.classList.add('thin-border');
    }
});

