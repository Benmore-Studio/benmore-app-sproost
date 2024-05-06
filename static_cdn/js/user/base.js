window.addEventListener("DOMContentLoaded", () => {
    handleDjangoMessages();
});

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
