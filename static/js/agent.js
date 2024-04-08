function openPropertyModal() {
    const modal = document.getElementById("modal-account-id")

    if (modal) {
        modal.classList.toggle("open")
    }
}

function closePropertyModal() {

    const modal = document.getElementById("modal-account-id")

    if (modal) {
        modal.classList.remove("open")
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const inputAccId = document.getElementById('account-id')
    inputAccId.addEventListener('input', addPropertyForm)
})

function addPropertyForm() {
    const inputAccId = document.getElementById('account-id')
    const addPropBtn = document.getElementById('add-property-btn')

    if (inputAccId.value === '') {
        addPropBtn.disabled = true
    } else {
        addPropBtn.disabled = false
    }
}

addPropertyForm()