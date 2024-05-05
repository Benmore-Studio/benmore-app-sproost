document.addEventListener("DOMContentLoaded", () => {
    handleHtmxErrors();
    handleDjangoMessages();
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
const handleDjangoMessages = () => {
    messages.forEach(function(message) {
        var color;
        switch(message.level) {
            case 'info':
                color = "blue";
                break;
            case 'error':
                color = "red";
                break;
            case 'warning':
                color = "orange";
                break;
            case 'success':
                color = "green";
                break;
            default:
                color = "black";
        }
        Toastify({
            text: message.text,
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
    });
}