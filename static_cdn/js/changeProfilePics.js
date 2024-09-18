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
const previewImage = document.getElementById('previewImageForm');
let galleryInput = document.getElementById('id_gallery_change')
let menuGalleryInput = document.getElementById('menu_id_gallery_change')
const captureButton = document.getElementById('capture');
const canvas = document.getElementById('canvas');
const loading = document.getElementById('loading');


// clicking on the profile pics to display it
img.onclick = function() {
  loading.style.display = "block";

  // Create a new Image element
  const image = new Image();

  // Set the source of the Image element
  image.crossOrigin = "Anonymous";
  image.src = this.src;

  // Event handler for when the image is loaded
  image.onload = function() {
      // Create a canvas element to draw the resized image
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');

      // Define maximum dimensions
      const maxWidth = 600;
      const maxHeight = 400;

      // Calculate new dimensions while maintaining aspect ratio
      let newWidth = image.width;
      let newHeight = image.height;

      const aspectRatio = newWidth / newHeight;
      if (newWidth > newHeight) {
          newWidth = maxWidth;
          newHeight = maxWidth / aspectRatio;
      } else {
          newHeight = maxHeight;
          newWidth = maxHeight * aspectRatio;
      }
      // Set canvas dimensions
      canvas.width = newWidth;
      canvas.height = newHeight;

      // Draw the resized image onto the canvas
      ctx.drawImage(image, 0, 0, newWidth, newHeight);

      // Convert the canvas content to a Blob
      canvas.toBlob(function(blob) {
          // Create a File object from the Blob
          const file = new File([blob], 'filename.jpg', { type: 'image/jpeg' });

          // Proceed with further processing, such as displaying the resized image
          modalImg.src = URL.createObjectURL(file);
      }, 'image/jpeg');

      loading.style.display = "none";
      modal.style.display = "block";
  };
 
};


// the x button that closes the modal
span.onclick = function() {
  modal.style.display = "none";
}

// the cancel button to stop the change through selecting pics from gallery
cancelDpChange.onclick = function() {
  modal.style.display = "none";
  sendButton.style.display = "none";
  dpView.style.display = "flex";
  previewImage.src = ''

}

// handling the process tht selects the image from my files and sends it to django
if(menuGalleryInput){
  menuGalleryInput.addEventListener('change', function(event) {
    // Get the selected file
    const selectedFile = event.target.files[0];
   

    // Display the selected image in the modal
    if(selectedFile){
      const previewImage = document.getElementById('previewImageForm');
      previewImage.src = URL.createObjectURL(selectedFile);

      dpView.style.display = "none";
      sendButton.style.display = "flex";
      modal.style.display = "block";
      // Call the resizeImage function to resize the image
      resizeImage(selectedFile, function(resizedImage) {
          // Set the source of the preview image to the resized image
          previewImage.src = resizedImage.src;
      });
    }
  });
}
if(galleryInput){
  galleryInput.addEventListener('change', function(event) {
    // Get the selected file
    const selectedFile = event.target.files[0];

    // Display the selected image in the modal
    if(selectedFile){
      const previewImage = document.getElementById('previewImageForm');
      previewImage.src = URL.createObjectURL(selectedFile);
      dpView.style.display = "none";
      sendButton.style.display = "flex";

      // Call the resizeImage function to resize the image
      resizeImage(selectedFile, function(resizedImage) {
          // Set the source of the preview image to the resized image
          previewImage.src = resizedImage.src;
      });
    }
  });
}

// Function to resize the image
function resizeImage(selectedFile, callback) {
  // Create a new FileReader
  const reader = new FileReader();

  // Define maximum dimensions
  const maxWidth = 800;
  const maxHeight = 600;

  reader.onload = function(e) {
      // Create an image element to load the selected file
      const img = new Image();

      // Image onload event handler
      img.onload = function() {
          // Create a canvas element to draw the resized image
          const canvas = document.createElement('canvas');
          const ctx = canvas.getContext('2d');

          // Calculate new dimensions while maintaining aspect ratio
          let newWidth = img.width;
          let newHeight = img.height;
          if (newWidth > maxWidth || newHeight > maxHeight) {
              const aspectRatio = newWidth / newHeight;
              if (newWidth > newHeight) {
                  newWidth = maxWidth;
                  newHeight = maxWidth / aspectRatio;
              } else {
                  newHeight = maxHeight;
                  newWidth = maxHeight * aspectRatio;
              }
          }

          // Set canvas dimensions
          canvas.width = newWidth;
          canvas.height = newHeight;

          // Draw the resized image onto the canvas
          ctx.drawImage(img, 0, 0, newWidth, newHeight);

          // Convert the canvas content to a Blob
          canvas.toBlob(function(blob) {
              // Create a new Image object from the Blob
              const resizedImage = new Image();
              resizedImage.src = URL.createObjectURL(blob);

              // Callback function with resized image as argument
              callback(resizedImage);
          }, 'image/jpeg');
      };

      // Load the selected file into the image element
      img.src = e.target.result;
  };

  // Read the selected file as a data URL
  reader.readAsDataURL(selectedFile);
}


// selecting image through camera
changeThroughCamera.onclick = function(){
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
          galleryInput.files = dataTransfer.files
        }else{
          alert("error")
        }
    }
    else{
      // alert('Video stream is not playing or has ended.');
      console.error('Video stream is not playing or has ended.');
    }
  });

// attaching the stop functiion to a click event
stopButton.addEventListener('click', stopfunction);

