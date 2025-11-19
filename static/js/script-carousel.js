// KARUZELA – uruchamiaj tylko wtedy, gdy elementy istnieją
const slides = document.querySelectorAll('.carousel-slide');

if (slides.length > 0) {
  let currentSlide = 0;
  const totalSlides = slides.length;
  let intervalId; // <- timer automatyczny

  const showSlide = (index) => {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
  };

  const restartTimer = () => {
    clearInterval(intervalId);
    intervalId = setInterval(() => {
      currentSlide = (currentSlide + 1) % totalSlides;
      showSlide(currentSlide);
    }, 7000);
  };

  const nextBtn = document.querySelector('.carousel-button.next');
  const prevBtn = document.querySelector('.carousel-button.prev');

  if (nextBtn && prevBtn) {
    nextBtn.addEventListener('click', () => {
      currentSlide = (currentSlide + 1) % totalSlides;
      showSlide(currentSlide);
      restartTimer(); // reset po kliknięciu
    });

    prevBtn.addEventListener('click', () => {
      currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
      showSlide(currentSlide);
      restartTimer(); // reset po kliknięciu
    });

    // Start timera na początku
    restartTimer();
  }
}
