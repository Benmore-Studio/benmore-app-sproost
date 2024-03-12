var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
    showStep(currentStep)
    uploadFiles()
})

function showStep(n) {
    // This function will display the specified tab of the form...
    var x = document.querySelectorAll("#step")

    x[n].style.display = "block"
        //... and fix the Previous/Next buttons:
    if (n === 0) {
        document.getElementById("prevBtn").style.display = "none"
    } else {
        document.getElementById("prevBtn").style.display = "block"
    }
    if (n == x.length - 1) {
        document.getElementById("nextBtn").innerHTML = "Confirm"
        clearSuccessMsg()
    } else if (n === 0) {
        document.getElementById("nextBtn").textContent = "Request Quotes"
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
    x = document.querySelectorAll("#step")
    y = x[currentStep].getElementsByTagName("input")
        // A loop that checks every input field in the current tab:
    if (y) {}

    return valid // return the valid status
}

function nextPrev(n) {
    // This function will figure out which tab to display
    var x = document.querySelectorAll("#step")
        //   if (n == 1 && !validateForm()) return false
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

function goBack() {
    history.back()
}

function clearSuccessMsg() {
    setTimeout(() => {
        location.href = "/"
    }, 2000)
}

function uploadFiles() {
    const fileContainer = document.getElementById('file-container')
    document.getElementById('upload-quote').addEventListener('change', function() {
        let fileInput = document.getElementById('upload-quote');
        let selectedFiles = fileInput.files
        let selectedFileNames = '';
        let selectedFileList = [];
        let photos = [];
        let videos = [];
        for (var i = 0; i < selectedFiles.length; i++) {
            selectedFileList.push(selectedFiles[i])
        }
        console.log({ selectedFiles });
        console.log({ selectedFileList });

        if (selectedFileList.length > 0) {
            photos = selectedFileList.filter((file) => file.type.startsWith('image/'))
            console.log({ photos });
            videos = selectedFileList.filter((file) => file.type.startsWith('video/'))
            console.log({ videos });

            photos.forEach(function(photo) {
                fileContainer.innerHTML += `
                <a href='${URL.createObjectURL(photo)}' class="w-[74px] h-[74px] rounded-md" download>
                    <img src="${URL.createObjectURL(photo)}" alt="" class="w-full h-full object-cover rounded-md">
                </a>
                `
            });

            videos.forEach(function(video) {

                fileContainer.innerHTML +=
                    `
               <div class="w-[74px] h-[74px] rounded-md relative">
                <img src="/static/images/vid-play-bg.jpg" alt="" class="w-full h-full object-cover rounded-md">
              <a href='${URL.createObjectURL(video)}' class="absolute top-5 left-5 right-5" download >                
              <img src="/static/svgs/Play-button.svg" alt="">
              </a>
           </div>
               `

            });
        }
    });
}