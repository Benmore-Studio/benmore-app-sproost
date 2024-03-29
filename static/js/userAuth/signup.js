 var currentStep = 0 // Current tab is set to be the first tab (0)
 window.addEventListener("DOMContentLoaded", () => {
     showStep(currentStep)
     selectUserType()
 })

 function showStep(n) {
     // This function will display the specified tab of the form...
     var x = document.getElementsByClassName("step")

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
     x = document.getElementsByClassName("step")
     y = x[currentStep].getElementsByTagName("input")
    // A loop that checks every input field in the current tab:
    if (currentStep === 0) {
        valid = [...y].some((input) => input.checked)
    }else{
        valid = [...y].every((input) => input.value !== "")
    }
    return valid
 }

 function nextPrev(n) {
     // This function will figure out which tab to display
     var x = document.getElementsByClassName("step")
     if (n == 1 && !validateForm()) {
        // if we get here it means, we are trying to go to the next step, but not all fields are filled
        let toastMsg = currentStep === 0 ? "please select one of the options before proceeding" : "please make sure all fields are filled before proceeding"
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
         // Hide the current tab:
     x[currentStep].style.display = "none"
         // Increase or decrease the current tab by 1:
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
     console.log({ radioBoxes });

     radioBoxes.forEach((radio, idx) => {
         radio.addEventListener('change', function() {
             if (radio.checked) {
                 parentDivs.forEach(div => div.classList.remove('active'));
                 parentDivs[idx].classList.add('active');
             } else {
                 parentDivs[idx].classList.remove('active');
             }
         });
     });


 }