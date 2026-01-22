/**
 * OBSŁUGA KARUZELI ARTYKUŁÓW NA STRONIE GŁÓWNEJ
 * 
 * Funkcjonalność:
 * - Automatyczne przełączanie slajdów co 7 sekund
 * - Ręczna nawigacja poprzez przyciski "poprzednia" i "następna"
 * - Reset timera przy kliknięciu przycisku
 */

// Pobieranie wszystkich slajdów karuzeli
const slides = document.querySelectorAll('.carousel-slide');

// Karuzela działa tylko jeśli istnieją slajdy
if (slides.length > 0) {
  let currentSlide = 0;                    // Indeks aktualnie wyświetlanego slajdu
  const totalSlides = slides.length;       // Liczba wszystkich slajdów
  let intervalId;                          // ID timera automatycznego przełączania

  /**
   * Wyświetla slajd o danym indeksie
   * Usuwa klasę 'active' ze wszystkich slajdów i dodaje ją do wybranego
   * @param {number} index - Indeks slajdu do wyświetlenia
   */
  const showSlide = (index) => {
    slides.forEach(slide => slide.classList.remove('active'));
    slides[index].classList.add('active');
  };

  /**
   * Restartuje timer automatycznego przełączania slajdów
   * Przełącza na następny slajd co 7 sekund
   */
  const restartTimer = () => {
    clearInterval(intervalId);  // Wyczyść stary timer
    intervalId = setInterval(() => {
      currentSlide = (currentSlide + 1) % totalSlides;  // Przejdź do następnego slajdu (zapętlanie)
      showSlide(currentSlide);
    }, 7000);  // 7000ms = 7 sekund
  };

  // Pobranie przycisków nawigacji
  const nextBtn = document.querySelector('.carousel-button.next');
  const prevBtn = document.querySelector('.carousel-button.prev');

  // Obsługa przycisków tylko jeśli istnieją
  if (nextBtn && prevBtn) {
    /**
     * Przycisk "Następna" - przejście do następnego slajdu
     */
    nextBtn.addEventListener('click', () => {
      currentSlide = (currentSlide + 1) % totalSlides;  // Increment ze zapętlaniem
      showSlide(currentSlide);
      restartTimer();  // Reset timer po kliknięciu użytkownika
    });

    /**
     * Przycisk "Poprzednia" - przejście do poprzedniego slajdu
     */
    prevBtn.addEventListener('click', () => {
      currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;  // Decrement ze zapętlaniem
      showSlide(currentSlide);
      restartTimer();  // Reset timer po kliknięciu użytkownika
    });

    // Rozpoczęcie automatycznego przełączania slajdów na starcie
    restartTimer();
  }
}
