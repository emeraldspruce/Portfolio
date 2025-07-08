function syncMainWidthWithNavbar() {
    const navbar = document.getElementById("navbar");
    if (!navbar) return;
    const navbarWidth = navbar.offsetWidth - 1 + "px";
    const navbarHeight = navbar.offsetHeight + "px";
    document.documentElement.style.setProperty('--navbar-width', navbarWidth);
    document.documentElement.style.setProperty('--navbar-height', navbarHeight);
}

window.addEventListener("load", syncMainWidthWithNavbar);
window.addEventListener("resize", syncMainWidthWithNavbar);
