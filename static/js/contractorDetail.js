document.addEventListener("DOMContentLoaded", function () {
  // By default, open the first tab
  document.getElementById("tab1").style.display = "block"
  document.getElementsByClassName("tablinks")[0].className += " active"
  handleImageUpload()
})

window.addEventListener("DOMContentLoaded", () => {
  uploadFiles()
})

async function handleImageUpload() {
  const uploadBtn = document.getElementById("upload-btn")
  const fileInput = document.getElementById("file-input")
  uploadBtn.addEventListener("click", function (e) {
    fileInput.click()
  })
  fileInput.addEventListener("change", async function (e) {
    const files = fileInput.files
    const formData = new FormData()

    for (let i = 0; i < files.length; i++) {
      if (!files[i].type.startsWith("image/")) {
        Toastify({
          text: "file must be an image",
          duration: 3000,
          close: true,
          gravity: "top",
          position: "left",
          stopOnFocus: true,
          style: {
            background: "red",
            maxWidth: "100%",
          },
        }).showToast()
        return
      }
      formData.append("images", files[i])
    }

    try {
      const response = await fetch("/profiles/upload-image/", {
        method: "POST",
        body: formData,
        headers: {
          "X-CSRFToken": csrf_token,
        },
      })

      if (!response.ok) {
        Toastify({
          text: "image upload failed",
          duration: 3000,
          close: true,
          gravity: "top",
          position: "left",
          stopOnFocus: true,
          style: {
            background: "red",
            maxWidth: "100%",
          },
        }).showToast()
      }
    } catch (err) {
      console.log(err)
      Toastify({
        text: "image upload failed",
        duration: 3000,
        close: true,
        gravity: "top",
        position: "left",
        stopOnFocus: true,
        style: {
          background: "red",
          maxWidth: "100%",
        },
      }).showToast()
    }
  })
}

function openTab(evt, tabName) {
  var i, tabcontent, tablinks
  tabcontent = document.getElementsByClassName("tabcontent")
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none"
  }
  tablinks = document.getElementsByClassName("tablinks")
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "")
  }
  document.getElementById(tabName).style.display = "block"
  evt.currentTarget.className += " active"
}

// By default, open the first tab
document.getElementById("tab1").style.display = "block"
document.getElementsByClassName("tablinks")[0].className += " active"

console.log("we are here")

function uploadFiles() {
  const fileContainer = document.getElementById("file-container")
  document.getElementById("upload-media").addEventListener("change", function () {
    let fileInput = document.getElementById("upload-media")
    let selectedFiles = fileInput.files
    let selectedFileList = []
    let photos = []
    let videos = []

    for (var i = 0; i < selectedFiles.length; i++) {
      selectedFileList.push(selectedFiles[i])
    }
    console.log({selectedFiles})
    console.log({selectedFileList})

    if (selectedFileList.length > 0) {
      photos = selectedFileList.filter((file) => file.type.startsWith("image/"))
      videos = selectedFileList.filter((file) => file.type.startsWith("video/"))

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
    }
  })
}

function removeFile(removeIcon) {
  // Get the parent container of the remove image
  var container = removeIcon.parentElement

  // Remove the parent container
  container.remove()
}
