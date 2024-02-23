var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
  showStep(currentStep)
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
    document.getElementById("nextBtn").innerHTML = "Submit"
  } else {
    document.getElementById("nextBtn").innerHTML = "Next"
  }
  //... and run a function that will display the correct step indicator:
  fixStepIndicator(n)
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("step")
  // Hide the current tab:
  x[currentStep].style.display = "none"
  // Increase or decrease the current tab by 1:
  currentStep = currentStep + n
  // if you have reached the end of the form...
  if (currentStep >= x.length) {
    // ... the form gets submitted:
    document.getElementById("registerForm").submit()
    return false
  }
  showStep(currentStep)
}

function fixStepIndicator(n) {
  // This function removes the "active" class of all steps...
  var i,
    x = document.getElementsByClassName("dot-step")
  for (i = 0; i < x.length; i++) {
    x[i].className = x[i].className.replace(" active", "")
  }
  //... and adds the "active" class on the current step:
  x[n].className += " active"
}
