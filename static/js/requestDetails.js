function goBack() {
    history.back();
}

function openQuotation() {
    const modal = document.getElementById("modal-quotation")

    if (modal) {
        modal.classList.toggle("open")
    }
}


function closeModal() {
    const modal = document.getElementById("modal-quotation")

    if (modal) {
        modal.classList.remove("open")
    }
}

let fieldCount = 1;

function addField() {
    fieldCount++;
    const newField = document.createElement('div');
    newField.innerHTML = `
    <div class="grid grid-cols-[60%37%] gap-4">
        <div class="w-full mt-5">
            <h4 class="mb-2 text-neutral-700">Quotation Item</h4>

            <div class="p-2 min-h-[45px] w-full flex items-center bg-white gap-4 border border-neutral-200 rounded-md">
                <input id="folder-title" type="email" placeholder="Input" required class="w-full focus-within:border-none outline-none bg-transparent" />
            </div>
        </div>
        <div class="w-full mt-5">
            <h4 class="mb-2 text-neutral-700">Price($)</h4>

            <div class="p-2 min-h-[45px] w-full flex items-center bg-white gap-4 border border-neutral-200 rounded-md">
                <input id="folder-title" type="email" placeholder="Input" required class="w-full focus-within:border-none outline-none bg-transparent" />
            </div>
        </div>
    </div>
  `;
    document.getElementById('dynamic-box').appendChild(newField);
}

function removeField() {
    if (fieldCount > 1) {
        const lastField = document.querySelector('#dynamic-box div:last-child');
        lastField.parentNode.removeChild(lastField);
        fieldCount--;
    }
}

function openSendQuotation() {
    const modal = document.getElementById("modal-send-quotation")

    if (modal) {
        modal.classList.toggle("open")
    }
}

function closeSendQuoteModal() {

    const modal = document.getElementById("modal-send-quotation")

    if (modal) {
        modal.classList.remove("open")
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const createQuoteBtn = document.getElementById("create-quote-btn")
    const sendQuoteBtn = document.getElementById("send-quote-btn")
    const editQuoteBtn = document.getElementById("edit-quote-btn")

    createQuoteBtn.addEventListener("click", () => {
        closeModal()
        openSendQuotation()
    });
    sendQuoteBtn.addEventListener("click", () => {
        // submit logic goes here
        closeSendQuoteModal()
    });

    editQuoteBtn.addEventListener("click", () => {
        closeSendQuoteModal()
        openQuotation()
    });

})