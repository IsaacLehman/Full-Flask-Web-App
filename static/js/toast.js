window.addEventListener('load', (event) => {
    console.log('page is fully loaded');
    var all_toasts = document.querySelectorAll(".toast");

    all_toasts.forEach(function (toast_ele) {
        new bootstrap.Toast(toast_ele).show();
        console.log(toast_ele);
    })
});


