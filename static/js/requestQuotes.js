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
  if (y) {
  }

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
  console.log("x&n: ", x, n, currentStep)
  // if you have reached the end of the form...
  if (currentStep >= x.length) {
    // ... the form gets submitted:
    console.log(document.getElementById("quoteRequestForm"))
    document.getElementById("quoteRequestForm").submit()
    return false
  }
  showStep(currentStep)
}

function submitQuote() {
  document.getElementById("quoteRequestForm").submit()
  return false
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
  const fileContainer = document.getElementById("file-container")
  var selectedFileList = [];
  var selectedFiles = [];
  document.getElementById("upload-quote").addEventListener("change", function () {
    let fileInput = document.getElementById("upload-quote")
    selectedFiles.push(...fileInput.files)
//    let selectedFileList = []
    let photos = []
    let videos = []
    let pdfs = []
    for (var i = 0; i < selectedFiles.length; i++) {
      selectedFileList.push(selectedFiles[i])
    }
    console.log({selectedFiles})
//    console.log({selectedFileList})


        console.log({selectedFileList});


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
  })


// Function to handle camera capture


document.getElementById("captureButton").addEventListener("click", function () {
    const constraints = {
      video: true,
    };

    navigator.mediaDevices.getUserMedia(constraints)
      .then(function (stream) {
        const video = document.createElement("video");
        video.srcObject = stream;
        video.onloadedmetadata = function (e) {
          video.play();
        };
        video.addEventListener("click", function () {
          const canvas = document.createElement("canvas");
          canvas.width = video.videoWidth;
          canvas.height = video.videoHeight;
          const context = canvas.getContext("2d");
          context.drawImage(video, 0, 0, canvas.width, canvas.height);
          const imageUrl = canvas.toDataURL("image/jpeg");

          // Display the captured photo
          fileContainer.innerHTML += `
            <div class="w-[74px] h-[74px] relative rounded-md">
              <img src="${imageUrl}" alt="" class="w-full h-full object-cover rounded-md">
              <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
            </div>
          `;

          // Stop the stream
          stream.getTracks().forEach(function (track) {
            track.stop();
          });

          // Remove the video element from the DOM
          video.remove();
        });
        document.body.appendChild(video);
      })
      .catch(function (err) {
        console.error("Error accessing camera: " + err);
      });
  });

//document.getElementById("captureButton").addEventListener("click", function () {
//  const constraints = {
//    video: true,
//  };
//
//  navigator.mediaDevices.getUserMedia(constraints)
//    .then(function (stream) {
//      const video = document.createElement("video");
//      video.srcObject = stream;
//      video.onloadedmetadata = function (e) {
//        video.play();
//      };
//      video.addEventListener("click", function () {
//        const canvas = document.createElement("canvas");
//        canvas.width = video.videoWidth;
//        canvas.height = video.videoHeight;
//        const context = canvas.getContext("2d");
//        context.drawImage(video, 0, 0, canvas.width, canvas.height);
//        const imageUrl = canvas.toDataURL("image/jpeg");
//
//        // Create a File object from the captured image data
//        const blob = dataURItoBlob(imageUrl);
//        let capturedImageFile = new File([blob], "captured_image_001.jpeg", { type: "image/jpeg" });
////        video.name = "uploaded-video";
//
//        // Append the video element to the form
//        const form = document.getElementById("quoteRequestForm");
//        form.appendChild(video);
//
//
//        // Display the captured photo
//        fileContainer.innerHTML += `
//          <div class="w-[74px] h-[74px] relative rounded-md">
//            <img src="${imageUrl}" alt="" class="w-full h-full object-cover rounded-md">
//            <img src="/static/images/remove.png" alt="" class="w-[16px] h-[16px] -top-2 -right-2 absolute object-cover rounded-full" onclick="removeFile(this)">
//          </div>
//        `;
//
//
//        // Create a hidden input field
//        const hiddenInput = document.getElementById("captured-image-input");
//        hiddenInput.type = "file";
//        hiddenInput.name = "captured-image"; // Set the name attribute as needed
//        hiddenInput.value = capturedImageFile; // Set the value to the captured image URL or Base64 data
//        hiddenInput.class = "hidden";
//        hiddenInput.files = capturedImageFile;
//        console.log(hiddenInput.files)
//
//
//        // Stop the stream
//        stream.getTracks().forEach(function (track) {
//          track.stop();
//        });
//
//        // Remove the video element from the DOM
//        video.remove();
//      });
//      document.body.appendChild(video);
//    })
//    .catch(function (err) {
//      console.error("Error accessing camera: " + err);
//    });
//});

// Function to convert data URI to Blob
function dataURItoBlob(dataURI) {
  const byteString = atob(dataURI.split(",")[1]);
  const mimeString = dataURI.split(",")[0].split(":")[1].split(";")[0];
  const ab = new ArrayBuffer(byteString.length);
  const ia = new Uint8Array(ab);
  for (let i = 0; i < byteString.length; i++) {
    ia[i] = byteString.charCodeAt(i);
  }
  return new Blob([ab], { type: mimeString });
}





}

function removeFile(removeIcon) {
  // Get the parent container of the remove image
  var container = removeIcon.parentElement

  // Remove the parent container
  container.remove()
}
