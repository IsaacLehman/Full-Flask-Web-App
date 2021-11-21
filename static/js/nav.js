const navbar = document.getElementById('main-nav');

window.addEventListener('scroll', function (e) {
    const lastPosition = window.scrollY;
    if (lastPosition > 40) {
        navbar.classList.add('nav-active');
        navbar.classList.add('bottom-shadow');
    } else if (navbar.classList.contains('nav-active')) {
        navbar.classList.remove('nav-active');
        navbar.classList.remove('bottom-shadow');
    } 
});


// initial check
if (window.scrollY > 40) {
    navbar.classList.add('nav-active');
    navbar.classList.add('bottom-shadow');
} else if (navbar.classList.contains('nav-active')) {
    navbar.classList.remove('nav-active');
    navbar.classList.remove('bottom-shadow');
}

// for blog single pages - reading progress
if (typeof isSingleBlog !== 'undefined') { // set in blog single template
    const progressBar = document.querySelector("#progressBar");
    let totalPageHeight = document.body.scrollHeight - window.innerHeight;
    // do initial set
    let newProgressHeight = (window.pageYOffset / totalPageHeight) * 100;
    progressBar.style.width = `${newProgressHeight}%`;
    progressBar.style.opacity = `${newProgressHeight}%`;
    // watch for scroll
    window.onscroll = () => {
        newProgressHeight = (window.pageYOffset / totalPageHeight) * 100;
        progressBar.style.width = `${newProgressHeight}%`;
        progressBar.style.opacity = `${newProgressHeight}%`;
    };
}