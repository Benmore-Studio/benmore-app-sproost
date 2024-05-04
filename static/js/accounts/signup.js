var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
    showStep(currentStep);
    selectUserType();
    validateEmail();
    validatePhoneNumber();
    validatePassword();
    validateRegistrationID();
})

function validateRegistrationID() {
    const regId = document.getElementById('registration_ID')
    const regIdError = document.getElementById('reg-id-error')
    regIdError.style.display = "none"
    regId.addEventListener('input', function (e) {
        const regId = e.target.value
        if (regId.length === 0) {
            regIdError.style.display = "block"
            regIdError.textContent = "Registration ID is required"
            regId.classList.add('focus:border-red-500');
            regId.classList.remove('focus:border-green-500');
        } else {
            regIdError.style.display = "none"
            regId.classList.remove('focus:border-red-500');
            regId.classList.add('focus:border-green-500');
        }
    })

}


function validatePassword() {
    password1 = document.getElementById('id_password1')
    password2 = document.getElementById('id_password2')
    passwordError = document.getElementById('password-error')
    passwordError.style.display = "none"

    password2.addEventListener('input', function (e) {
        password2.classList.remove('focus:border-gray-500');
        if (password1.value !== password2.value) {
            passwordError.textContent = "Passwords do not match"
            passwordError.style.display = "block"
            password2.classList.add('focus:border-red-500');
            password2.classList.remove('focus:border-green-500');
        } else {
            passwordError.style.display = "none"
            password2.classList.remove('focus:border-red-500');
            password2.classList.add('focus:border-green-500');
        }
    })
}

function validateEmail() {
    const emailError = document.getElementById('email-error')
    const emailInput = document.getElementById('id_email')
    emailError.style.display = "none"
    emailInput.addEventListener('input', function (e) {
        var email = e.target.value;
        var pattern = /^[^ ]+@[^ ]+\.[a-z]{2,3}$/;
        e.target.classList.remove('focus:border-gray-500');


        if (email.match(pattern)) {
            console.log("green")
            e.target.classList.remove('focus:border-red-500');
            e.target.classList.add('focus:border-green-500');
            emailError.style.display = "none"
        } else {
            console.log("red")
            e.target.classList.remove('focus:border-green-500');
            e.target.classList.add('focus:border-red-500');
            emailError.textContent = "Please enter a valid email address"
            emailError.style.display = "block"
        }
    });

}

async function checkPhoneNumber(phone, location) {
    const phoneError = document.getElementById('phone-error')
    const phoneField = document.getElementById('phone-field')

    phoneField.classList.remove('border-gray-300');
    try {
        const response = await fetch(`/accounts/validate-phone?phone=${phone}&location=${location}`)
        const data = await response.json()
        if (!response.ok || phone === ""){
            const message = data?.message || "Please provide a valid phone number"
            phoneError.style.display = "block"
            phoneError.textContent = message
            phoneField.classList.add('border-red-500');
            phoneField.classList.remove('border-green-500');
        }else{
            phoneError.style.display = "none"
            phoneField.classList.remove('border-red-500');
            phoneField.classList.add('border-green-500');
        }
    } catch (error) {
        console.log(error)
        phoneField.classList.add('border-red-500');
        phoneField.classList.remove('border-green-500');
        phoneError.textContent = "An error occurred while validating phone number"
    }
}

function validatePhoneNumber() {
    const phoneInput1 = document.getElementById('id_phone_number_1')
    const phonelocation = document.getElementById('id_phone_number_0')

    phoneInput1.addEventListener('input', async function (e) {
        // make ajax request to validate phone number
        const phone = e.target.value;
        const location = phonelocation.value;
        checkPhoneNumber(phone, location)
    })
    phonelocation.addEventListener('change', async function (e) {
        const phone = phoneInput1.value;
        const location = e.target.value;
        if (phone === "") {
            return
        }
        checkPhoneNumber(phone, location)
    })
}

function showStep(n) {
    //  check if the radio btn with name user_type has the value CO 
    const userType = document.querySelector('input[name="user_type"]:checked')
    if (userType && userType.value === "CO") {
        var x = document.getElementsByClassName("step-contractor")
    }else if(userType && userType.value === "AG"){
        var x = document.getElementsByClassName("step-agent")
    }else{
        var x = document.getElementsByClassName("step")
    }

    x[n].style.display = "block"
    //... and fix the Previous/Next buttons:
    if (n === 0) {
        document.getElementById("prevBtn").style.display = "none"
    } else {
        document.getElementById("prevBtn").style.display = "block"
    }

    if (n == x.length - 1) {
        document.getElementById("nextBtn").innerHTML = "Complete"
    } else if (n === 0) {
        document.getElementById("nextBtn").textContent = "Continue"
    } else {
        document.getElementById("nextBtn").textContent = "Next"
    }
}

function validateForm() {
    // This function deals with validation of the form fields
    var x,
        y,
        i,
        valid = false

    const userType = document.querySelector('input[name="user_type"]:checked')
    if (userType && userType.value === "CO") {
        var x = document.getElementsByClassName("step-contractor")
    }else if(userType && userType.value === "AG"){
        var x = document.getElementsByClassName("step-agent")
    }else{
        var x = document.getElementsByClassName("step")
    }

    y = x[currentStep].getElementsByTagName("input")
    // A loop that checks every input field in the current tab:
    if (currentStep === 0) {
        valid = [...y].some((input) => input.checked)
    } else if (currentStep === 1) {
        valid = [...y].some((input) => input.value !== "")
    }else{
        valid = [...y].every((input) => input.value !== "")
    }
    return valid
}

function nextPrev(n) {
    // This function will figure out which tab to display
    const userType = document.querySelector('input[name="user_type"]:checked')
    if (userType && userType.value === "CO") {
        var x = document.getElementsByClassName("step-contractor")
    }else if(userType && userType.value === "AG"){
        var x = document.getElementsByClassName("step-agent")
    }else{
        var x = document.getElementsByClassName("step")
    }
    
    if (n == 1 && !validateForm()) {
        // if we get here it means, we are trying to go to the next step, but not all fields are filled
        let toastMsg = currentStep === 0 ? "Please select one of the options before proceeding" : "Please make sure required fields are filled out before proceeding"
        Toastify({
            text: toastMsg,
            duration: 3000,
            close: true,
            gravity: "top",
            position: "left",
            stopOnFocus: true,
            style: {
                background: "orange",
                maxWidth: "100%",
            },
        }).showToast();
        return false
    }

    
    x[currentStep].style.display = "none"

    currentStep = currentStep + n
    
    // if you have reached the end of the form...
    if (currentStep >= x.length) {
        // ... the form gets submitted:
        document.getElementById("signupForm").submit()
        return false
    }
    showStep(currentStep)
}


function selectUserType() {
    const inputs = document.getElementsByTagName('input');
    const parentDivs = document.querySelectorAll('#container-check');
    const radioBoxes = Array.from(inputs).filter(input => input.type === 'radio');

    radioBoxes.forEach((radio, idx) => {
        radio.addEventListener('change', function () {
            if (radio.checked) {
                parentDivs.forEach(div => div.classList.remove('active'));
                parentDivs[idx].classList.add('active');
            } else {
                parentDivs[idx].classList.remove('active');
            }
        });
    });


}