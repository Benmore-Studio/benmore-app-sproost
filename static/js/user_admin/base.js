document.addEventListener("DOMContentLoaded", () => {
    handleHtmxErrors();
})

const handleHtmxErrors = () => {
    document.body.addEventListener('htmx:responseError', function (event) {
        const allowedErrors = ["statusSelectInput"]
        if (allowedErrors.includes(event.detail.elt.id)) {
            const message = event.detail.xhr.response
            DisplayErrors(message, "red")
        }
    });
}

const DisplayErrors = (msg, color) => {
    console.log("hello")
    Toastify({
        text: msg,
        duration: 3000,
        close: true,
        gravity: "top",
        position: "left",
        stopOnFocus: true,
        style: {
            background: color,
            maxWidth: "100%",
        },
        onClick: function(){}
    }).showToast();
}