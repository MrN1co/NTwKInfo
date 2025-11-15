// static/icons.js
function iconUrl(code) {
  if (!code) {
    return "https://openweathermap.org/img/wn/01d@2x.png"; // domyślna
  }
  return `https://openweathermap.org/img/wn/${code}@2x.png`;
}

