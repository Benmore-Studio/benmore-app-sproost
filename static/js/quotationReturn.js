var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
  showStep(currentStep)
})

function showStep(n) {
  var x = document.querySelectorAll("#step")

  x[n].style.display = "block"
  if (n === 0) {
    document.getElementById("prevBtn").style.display = "none"
  } else {
    document.getElementById("prevBtn").style.display = "block"
  }
  if (n == x.length - 1) {
    document.getElementById("nextBtn").innerHTML = "Confirm"
    clearSuccessMsg()
  } else if (n === 0) {
    document.getElementById("nextBtn").textContent = "Accept Quotes"
  } else {
    document.getElementById("nextBtn").textContent = "Next"
  }
}

function nextPrev(n) {
  var x = document.querySelectorAll("#step")

  x[currentStep].style.display = "none"
  currentStep = currentStep + n
  if (currentStep >= x.length) {
    document.getElementById("signupForm").submit()
    return false
  }
  showStep(currentStep)
}

function goBack() {
  history.back()
}
