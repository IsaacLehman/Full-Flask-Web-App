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