  var currentStep = 0 // Current tab is set to be the first tab (0)
window.addEventListener("DOMContentLoaded", () => {
  showStep(currentStep)
  uploadFiles()
  validateForm()
})


function validateForm() {
  // This function deals with validation of the form fields
  var x,
    y,
    i,
    valid = false
  x = document.querySelectorAll("#step")
  y = x[currentStep].getElementsByTagName("input")
  let requiredInputs = document.getElementsByClassName("input")
  let requiredInputsResult = Array.from(requiredInputs);
  valid = [...requiredInputsResult].every((input) => input.value !== "")

  return valid // return the valid status
}



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



function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.querySelectorAll("#step")
  //   if (n == 1 && !validateForm()) return false
  // Hide the current tab:
  x[currentStep].style.display = "none"
  // Increase or decrease the current tab by 1:
  
  // if you have reached the end of the form...
  if (currentStep <= 0) {
    if(!validateForm()){
      currentStep = currentStep + 0
      Toastify({
            text: 'Please make sure title and summary fields are filled out before proceeding',
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
    }else{
      currentStep = currentStep + n
    }
  }else{
    currentStep = currentStep + n
  }
  if (currentStep >= x.length) {
    // ... the form gets submitted:
    document.getElementById("quoteRequestForm").submit()
    return false
  }
  showStep(currentStep)
}

function submitQuote() {
  document.getElementById("quoteRequestForm").submit()
  return false
}

function goBacks() {
  history.back()
}

function clearSuccessMsg() {
  setTimeout(() => {
    location.href = "/"
  }, 2000)
}

let selectedFileList = []

function uploadFiles() {
  const fileContainer = document.getElementById("file-container") 
  const fileContainerCapture = document.getElementById("file-container-capture") 
  const quoteRequestForm = document.getElementById("quoteRequestForm")

  let captureInputId = 1

  // Function to handle camera capture
  // document.getElementById('captureButton').addEventListener('click', function() {
  //   // Trigger the file input click event

  //   // Create the capture input element
  //   var captureInput = document.createElement('input');
  //   captureInput.setAttribute('type', 'file');
  //   captureInput.setAttribute('id', `upload-capture-${captureInputId}`);
  //   captureInput.setAttribute('accept', 'image/*');
  //   captureInput.setAttribute('multiple', 'multiple');
  //   captureInput.setAttribute('name', 'upload-capture');
  //   captureInput.setAttribute('capture', 'environment');
  //   captureInput.classList.add('hidden');

  //   // Append the file input element to the form
  //   quoteRequestForm.appendChild(captureInput);

  //   captureInputId += 1

  //   captureInput.click();

  // captureInput.addEventListener('change', function(event) {
  //   const newFiles = event.target.files;

  //   if (newFiles && newFiles.length > 0) {
  //     let photo = newFiles[0]

  //     fileContainerCapture.innerHTML += `
  //       <div class="w-[74px] h-[74px] relative rounded-md">
  //       <a href='${URL.createObjectURL(photo)}' download>
  //           <img src="${URL.createObjectURL(photo)}" alt="" class="w-full h-full object-cover rounded-md">
  //       </a>
  //       <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
  //       </div>
  //       `
  //     }

  //   })
  // });

  document.getElementById("upload-quote").addEventListener("change", function () {
    let fileInput = document.getElementById("upload-quote")
    let selectedFiles = fileInput.files

    let photos = []
    let videos = []
    let pdfs = []

    // Clear the fileContainer before adding new files
    fileContainer.innerHTML = '';

    for (var i = 0; i < selectedFiles.length; i++) {
      selectedFileList.push(selectedFiles[i])
    }
    if (selectedFileList.length > 0) {
      photos = selectedFileList.filter((file) => file.type.startsWith("image/"))
      videos = selectedFileList.filter((file) => file.type.startsWith("video/"))
      pdfs = selectedFileList.filter((file) => file.type.startsWith("application/pdf"))

      photos.forEach(function (photo) {
        fileContainer.innerHTML += `
                <div class="w-[74px] h-[74px] relative rounded-md">
                <a href='${URL.createObjectURL(photo)}' download>
                    <img src="${URL.createObjectURL(photo)}" alt="" class="w-full h-full object-cover rounded-md">
                </a>
                <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
                </div>
                `
      })

      videos.forEach(function (video) {
        fileContainer.innerHTML += `
                <div class="w-[74px] h-[74px] rounded-md relative">
                    <img src="/static/images/vid-play-bg.jpg" alt="" class="w-full h-full object-cover rounded-md">
                    <a href='${URL.createObjectURL(video)}' class="absolute top-5 left-5 right-5" download >
                    <img src="/static/svgs/Play-button.svg" alt="">
                    </a>
                    <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
                </div>
               `
      })

      pdfs.forEach(function (pdf) {
        fileContainer.innerHTML += `
                <div class="w-[74px] h-[74px] rounded-md relative">
                    <img src="/static/images/pdf-icon.png" alt="" class="w-full h-full object-cover rounded-md">
                    <a href='${URL.createObjectURL(pdf)}' class="absolute top-5 left-5 right-5" download >PDF</a>
                    <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
                </div>
               `
      })
    }
    selectedFileList = []
  })
}

function removeFile(removeIcon) {
  // Get the parent container of the remove image
  var container = removeIcon.parentElement

  // Remove the parent container
  container.remove()
}

// recording video

  const videoPreview = document.getElementById("videoPreview");
const startRecordingButton = document.getElementById("startRecording");
const stopRecordingButton = document.getElementById("stopRecording");
const uploadVideoButton = document.getElementById("uploadVideo");
const uploadStatus = document.getElementById("uploadStatus");
const videoInput = document.getElementById('recordedVideoInput');

let mediaRecorder;
let recordedChunks = [];
let stream;

startRecordingButton.addEventListener("click", startRecording);
stopRecordingButton.addEventListener("click", stopRecording);
uploadVideoButton.addEventListener("click", handleRecordedVideo);

async function startRecording() {
    try {
      videoPreview.style.display = 'block'
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        videoPreview.srcObject = stream;
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const videoBlob = new Blob(recordedChunks, { type: "video/webm" });
            recordedChunks = [];
            const videoFile = new File([videoBlob], 'recorded-video.webm', { type: "video/webm" });

            // Create a DataTransfer object to hold the video file
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(videoFile);

            // Assign the video file to the hidden input
            videoInput.files = dataTransfer.files;

            // uploadVideoButton.disabled = false;
            uploadStatus.textContent = 'Video attached successfully!';
            uploadStatus.style.color = 'green';
        };

        mediaRecorder.start();
        startRecordingButton.disabled = true;
        stopRecordingButton.disabled = false;
    } catch (error) {
        console.error("Error starting recording:", error);
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        stream.getTracks().forEach(track => track.stop());
        videoPreview.srcObject = null;
        startRecordingButton.disabled = false;
        stopRecordingButton.disabled = true;
    }
    videoPreview.style.display = 'none'
}

function handleRecordedVideo() {
    // The video file is already attached to the hidden input
}

