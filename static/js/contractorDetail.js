document.addEventListener('DOMContentLoaded', function () {
  // By default, open the first tab
  document.getElementById("tab1").style.display = "block"
  document.getElementsByClassName("tablinks")[0].className += " active"
  handleImageUpload()

})

async function handleImageUpload() {
  const uploadBtn = document.getElementById('upload-btn')
  const fileInput = document.getElementById('file-input')
  uploadBtn.addEventListener('click', function (e) {
    fileInput.click()
  })
  fileInput.addEventListener('change', async function (e) {
    const files = fileInput.files;
    const formData = new FormData();
    

    for (let i = 0; i < files.length; i++) {
      if (!files[i].type.startsWith('image/')) {
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
        }).showToast();
        return;
      }
      formData.append('images', files[i]);
    }

    try {
      const response = await fetch('/profiles/upload-image/', {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrf_token
        }
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
        }).showToast();
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
      }).showToast();
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


