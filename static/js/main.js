// Funkcja do automatycznego odświeżania strony co 60 sekund ~ KG
function autoRefresh() {
    setTimeout(function() {
        location.reload();
    }, 60000); // w milisekundach
}

// Uruchomienie auto-odświeżania po załadowaniu strony ~ KG
window.onload = autoRefresh;
console.log('JavaScript załadowany');//debug