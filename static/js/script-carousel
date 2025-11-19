// KARUZELA – uruchamiaj tylko wtedy, gdy elementy istnieją
const slides = document.querySelectorAll('.carousel-slide');

if (slides.length > 0) {
  let currentSlide = 0;
  const totalSlides = slides.length;

  const showSlide = (index) => {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
  };

  const nextBtn = document.querySelector('.carousel-button.next');
  const prevBtn = document.querySelector('.carousel-button.prev');

  if (nextBtn && prevBtn) {
    nextBtn.addEventListener('click', () => {
      currentSlide = (currentSlide + 1) % totalSlides;
      showSlide(currentSlide);
    });

    prevBtn.addEventListener('click', () => {
      currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
      showSlide(currentSlide);
    });

    // Automatyczne przewijanie
    setInterval(() => {
      currentSlide = (currentSlide + 1) % totalSlides;
      showSlide(currentSlide);
    }, 7000);
  }
}
