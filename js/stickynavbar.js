var navbar = document.getElementById('navbar-mine');

if(navbar===null)
    navbar = document.getElementById('navbar-special');

window.addEventListener('scroll', function(){
    let sticky = navbar.offsetTop;
    if(window.pageYOffset >= sticky){
        navbar.style.position = "fixed";
        navbar.style.top = "0px";
    }
});

function hoverEffect(e){
    e.style.background = "#ffffff";
    e.style.color = "#000000";
}

function cancelHover(e){
    e.style.background = "";
    e.style.color = "#ffffff";
}