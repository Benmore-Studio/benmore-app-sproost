let modal = document.getElementById("imagePreviewModal");
let img = document.getElementById("profilepicture");
let dpView = document.getElementById("dp-view");
let modalImg = document.getElementById("previewImage");
let sendButton = document.getElementById("send-button");
let cancelDpChange = document.getElementById("cancel-dp-change");
let changeThroughCamera = document.getElementById("change-through-camera");
let captureVideoModal = document.getElementById("capture-video");
let span = document.getElementsByClassName("close")[0];
let stopButton = document.getElementById("stop");
let galleryInput = document.getElementById('id_gallery_change')
const captureButton = document.getElementById('capture');
const canvas = document.getElementById('canvas');


// clicking on the profile pics to display it
img.onclick = function(){
  modal.style.display = "block";
  modalImg.src = this.src;
  console.log("too faith");
}

// the x button that closes the modal
span.onclick = function() {
  modal.style.display = "none";
}

// the cancel button to stop the change through selecting pics from gallery
cancelDpChange.onclick = function() {
  modal.style.display = "none";
}

// handling the process tht selects the image from my files and sends it to django
galleryInput.addEventListener('change', function(event) {
    // Get the selected file
    const selectedFile = event.target.files[0];
    console.log(selectedFile);

    // Display the selected image in the modal
    if(selectedFile){
      const previewImage = document.getElementById('previewImageForm');
      previewImage.src = URL.createObjectURL(selectedFile);
      dpView.style.display = "none";
      sendButton.style.display = "flex";
    }

    
});


// selecting image through camera
changeThroughCamera.onclick = function(){
  console.log("object");
  modal.style.display = "none";
  captureVideoModal.style.display = "block";
  const video = document.getElementById('video');

  // Access the camera stream
  navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
          video.srcObject = stream;
      })
      .catch(error => {
        console.error('Error accessing the camera:', error);
    });

  }


  // function to stop the camera
  function stopfunction(){
      console.log("stop record");
      captureVideoModal.style.display = "none";
      // Stop the camera stream
      video.srcObject.getTracks().forEach(track => {
          track.stop();
      });
  }


  // Add click event listener to the capture button
captureButton.addEventListener('click', () => {
    // to ensure that the video stream is playing
    if (!video.paused && !video.ended) {
        // Get the canvas context
        const ctx = canvas.getContext('2d');
        
        // Draw the current frame of the video onto the canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // extracting the captured image data from the canvas
        const imageData = canvas.toDataURL('image/png');
        
        // Convert the Base64 string to a Blob object
        let byteCharacters = atob(imageData.split(',')[1]);
        let byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        let byteArray = new Uint8Array(byteNumbers);
        let blob = new Blob([byteArray], { type: 'image/png' });

        // Create a blob URL for the Blob object
        let blobUrl = URL.createObjectURL(blob);

        // Set the blob URL as the src attribute of an image element, so it can be previewed
        const previewImage = document.getElementById('previewImageForm');
        previewImage.src = "";
        if(blobUrl){
          previewImage.src = blobUrl;
          captureVideoModal.style.display = "none";
          dpView.style.display = "none";
          modal.style.display = "block";
          sendButton.style.display = "flex";
          stopfunction()
          const file = new File([blob], 'profilepics.png', { type: 'image/png' });
         // Create a DataTransfer object
          const dataTransfer = new DataTransfer();

          // Add the file to the DataTransfer object
          dataTransfer.items.add(file);
          // galleryInput.files = dataTransfer.files
          // console.log(imageData);
          // console.log(blobUrl);
          // console.log(previewImage);
        }else{
          alert("error")
        }
    }
    else{
      alert('Video stream is not playing or has ended.');
      console.error('Video stream is not playing or has ended.');
    }
  });

// attaching the stop functiion to a click event
stopButton.addEventListener('click', stopfunction);

