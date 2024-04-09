function handleMobileNav() {
    const navItems = document.querySelectorAll("#mobile_navItem")
    const mobileNavContainer = document.getElementById("mobileNav")

    navItems.forEach((navItem) => {
        navItem.addEventListener("click", () => {
            mobileNavContainer.classList.remove("active")
        })
    })
}

function toggleMobileNavbar() {
    const mobileNavContainer = document.getElementById("mobileNav")
    mobileNavContainer.classList.toggle("active")
}