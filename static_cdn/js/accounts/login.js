window.addEventListener('DOMContentLoaded', () => {
    handleLoginSubmit();
})


function handleLoginSubmit() {
    // dsiables btn after login btn is clicked
    const loginBtn = document.getElementById('loginBtn');
    const loginForm = document.getElementById('loginForm');
    const Spinner = document.getElementById("spinner");
    loginForm.addEventListener('submit', (e) => {
        loginBtn.disabled = true;
        loginBtn.classList.add('opacity-50', 'cursor-not-allowed');
        Spinner.classList.remove("hidden");
    });
}