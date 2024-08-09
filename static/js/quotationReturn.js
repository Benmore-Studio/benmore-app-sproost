var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
    showStep(currentStep)
    uploadFiles()
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


function uploadFiles() {
    const fileContainer = document.getElementById('file-container')
    document.getElementById('upload-quote').addEventListener('change', function() {
        let fileInput = document.getElementById('upload-quote');
        let selectedFiles = fileInput.files
        let selectedFileList = [];
        let photos = [];
        let videos = [];
        for (var i = 0; i < selectedFiles.length; i++) {
            selectedFileList.push(selectedFiles[i])
        }

        if (selectedFileList.length > 0) {
            photos = selectedFileList.filter((file) => file.type.startsWith('image/'))
            videos = selectedFileList.filter((file) => file.type.startsWith('video/'))

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