// let slideIndex = 1
// const slides = document.querySelectorAll(".carousel-item")
// const indicators = document.querySelectorAll(".indicator")
// const totalSlides = slides.length

// function showSlides() {
//   if (slideIndex > totalSlides) {
//     slideIndex = 1
//   }
//   if (slideIndex < 1) {
//     slideIndex = totalSlides
//   }
//   for (let i = 0; i < slides.length; i++) {
//     slides[i].style.display = "none"
//   }
//   for (let i = 0; i < indicators.length; i++) {
//     indicators[i].classList.remove("active")
//   }
//   slides[slideIndex - 1].style.display = "block"
//   indicators[slideIndex - 1].classList.add("active")
// }

// function currentSlide(n) {
//   slideIndex = n
//   showSlides()
// }

// function nextSlide() {
//   slideIndex++
//   showSlides()
// }

// function prevSlide() {
//   slideIndex--
//   showSlides()
// }

// // Autoplay
// let autoplayInterval = setInterval(nextSlide, 2000)

// // Stop autoplay when mouse hovers over carousel
// const carouselContainer = document.querySelector(".carousel-container")
// carouselContainer.addEventListener("mouseenter", () => {
//   clearInterval(autoplayInterval)
// })

// // Resume autoplay when mouse leaves carousel
// carouselContainer.addEventListener("mouseleave", () => {
//   autoplayInterval = setInterval(nextSlide, 2000)
// })

// // Show first slide initially
// showSlides()
