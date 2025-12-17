(function () {
    // run after DOM ready to ensure elements exist
    function init() {
        const RATES =
            (window.ECON_DATA && window.ECON_DATA.currency_rates) || {};

        const amountEl = document.getElementById("amount");
        const fromEl = document.getElementById("currency-from");
        const toEl = document.getElementById("currency-to");
        const resultEl = document.getElementById("result");

        // Formatowanie wyniku: zawsze 2 miejsca po przecinku (zaokrąglone)
        const PL_FORMATTER = new Intl.NumberFormat("pl-PL", {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        });

        function compute() {
            const raw = amountEl.value.trim();
            if (raw === "") {
                resultEl.value = "";
                return;
            }

            const hasTrailingSep = /[.,]$/.test(raw);
            const normalized = raw.replace(",", ".");
            const a = parseFloat(normalized);

            if (isNaN(a)) {
                resultEl.value = "";
                return;
            }

            const from = fromEl.value || "PLN";
            const to = toEl.value || "PLN";

            const rateFrom = RATES[from] !== undefined ? RATES[from] : 1;
            const rateTo = RATES[to] !== undefined ? RATES[to] : 1;

            const inPln = a * rateFrom;
            const res = inPln / rateTo;

            // zaokrąglij numerycznie do 2 miejsc przed formatowaniem
            const rounded = Math.round(res * 100) / 100;
            let formatted = PL_FORMATTER.format(rounded);
            if (hasTrailingSep) {
                // Only append a trailing comma when the formatted value has no decimal separator yet.
                if (!formatted.includes(",")) {
                    formatted = formatted + ",";
                }
            }

            resultEl.value = formatted;
        }

        function enforceTwoDecimals() {
            let raw = amountEl.value;
            if (!raw) return;

            const MAX_DIGITS = 9; // maksymalna liczba cyfr (bez separatorów)

            // remember if user typed a trailing separator (dot or comma)
            const hadTrailingSep = /[.,]$/.test(raw);

            // remove any characters except digits and separators
            let s = raw.replace(/[^0-9.,]/g, "");

            // normalize commas to dot for processing
            let normalized = s.replace(/,/g, ".");

            // keep only the first dot, remove further dots
            const firstDot = normalized.indexOf(".");
            if (firstDot !== -1) {
                normalized =
                    normalized.slice(0, firstDot + 1) +
                    normalized.slice(firstDot + 1).replace(/\./g, "");
            }

            // limit to two decimal places if dot present
            if (normalized.indexOf(".") !== -1) {
                const [intPart, decPart = ""] = normalized.split(".");
                const dec = decPart.slice(0, 2);
                // if user had trailing separator, keep a trailing dot to indicate they typed it
                normalized =
                    intPart +
                    (dec.length > 0 ? "." + dec : hadTrailingSep ? "." : "");
            }

            // Enforce total digits (integer + fractional) <= MAX_DIGITS
            // Remove extra digits from the end while preserving the dot.
            const digitsOnly = normalized.replace(/[^0-9]/g, "");
            if (digitsOnly.length > MAX_DIGITS) {
                let over = digitsOnly.length - MAX_DIGITS;
                // Remove last 'over' digit characters from normalized
                while (over > 0) {
                    let lastIndex = -1;
                    for (let i = normalized.length - 1; i >= 0; i--) {
                        if (/\d/.test(normalized[i])) {
                            lastIndex = i;
                            break;
                        }
                    }
                    if (lastIndex === -1) break;
                    normalized =
                        normalized.slice(0, lastIndex) +
                        normalized.slice(lastIndex + 1);
                    over--;
                }
                // If result ends with a dot and it wasn't intended as trailing sep, keep it only if hadTrailingSep
                if (normalized.endsWith(".") && !hadTrailingSep) {
                    normalized = normalized.slice(0, -1);
                }
            }

            // Update the input value (uses dot as separator for consistency in parsing)
            amountEl.value = normalized;
        }

        if (amountEl)
            amountEl.addEventListener("input", function () {
                enforceTwoDecimals();
                compute();
            });
        if (fromEl) fromEl.addEventListener("change", compute);
        if (toEl) toEl.addEventListener("change", compute);

        // Optional: button to trigger compute for users who click it
        document
            .querySelectorAll(".calc-box .btn")
            .forEach((btn) => btn.addEventListener("click", compute));

        // swap handler
        const swapBtn = document.getElementById("swap-btn");
        if (swapBtn) {
            swapBtn.addEventListener("click", function () {
                const valFrom = fromEl.value;
                const valTo = toEl.value;

                // helper: ensure select contains option with given value
                function ensureOption(sel, val) {
                    if (val === undefined || val === null || val === "") return;
                    for (let i = 0; i < sel.options.length; i++) {
                        if (sel.options[i].value === val) return;
                    }
                    // add new option (label == value)
                    const opt = new Option(val, val);
                    sel.add(opt);
                }

                // ensure both selects can accept swapped values
                ensureOption(fromEl, valTo);
                ensureOption(toEl, valFrom);

                // perform swap
                fromEl.value = valTo;
                toEl.value = valFrom;

                // recompute result and focus amount
                compute();
                amountEl.focus();
            });
        }

        compute();
    }

    // Dynamic currency chart loading
    function setupChartLoader() {
        const toEl = document.getElementById("currency-to");
        const chartImg = document.querySelector(".currency-chart");

        if (!toEl || !chartImg) return;

        toEl.addEventListener("change", function () {
            const currency = toEl.value;

            // Show loading state
            chartImg.style.opacity = "0.5";

            // Fetch new chart
            fetch(`/ekonomia/chart/${currency}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data.success && data.chart) {
                        chartImg.src = `data:image/png;base64,${data.chart}`;
                        chartImg.style.opacity = "1";
                    } else {
                        alert(
                            data.message || `Brak danych dla waluty ${currency}`
                        );
                        chartImg.style.opacity = "1";
                    }
                })
                .catch((error) => {
                    console.error("Error loading chart:", error);
                    alert("Błąd podczas ładowania wykresu");
                    chartImg.style.opacity = "1";
                });
        });
    }

    // Favorite currency functionality (inspired by weather favorites)
    function setupFavoriteCurrency() {
        console.log('setupFavoriteCurrency called');
        
        // Helper: fetch with X-Requested-With header for AJAX
        const apiCall = (url, options = {}) => {
            return fetch(url, {
                credentials: 'same-origin',
                ...options,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    ...(options.headers || {})
                }
            });
        };
        
        // Try multiple times to find boxes in case of slow rendering
        function initFavoritesSetup() {
            const container = document.querySelector('.currency-scroll');
            const currencyBoxes = document.querySelectorAll('.currency-box[data-currency]');
            
            console.log('Container found:', !!container);
            console.log('Currency boxes found:', currencyBoxes.length);
            
            if (currencyBoxes.length === 0 || !container) {
                console.warn('setupFavoriteCurrency: no boxes or container found, retrying...');
                setTimeout(initFavoritesSetup, 100);
                return;
            }

            console.log('Currency boxes found:', Array.from(currencyBoxes).map(b => b.dataset.currency));

            // Load available currencies from API (10 currencies with rates)
            async function loadAvailableCurrencies() {
                try {
                    const res = await apiCall('/ekonomia/api/exchange-rates');
                    if (!res.ok) return [];
                    const data = await res.json();
                    console.log('Available currencies loaded:', data);
                    return data || [];
                } catch (e) {
                    console.warn('Failed to fetch available currencies', e);
                    return [];
                }
            }

            // Store available currencies globally for use in modal and reordering
            let availableCurrenciesCache = [];

            // Fetch and display favorite currencies on page load
            async function loadFavorites() {
                try {
                    // Load available currencies first if not cached
                    if (availableCurrenciesCache.length === 0) {
                        availableCurrenciesCache = await loadAvailableCurrencies();
                    }

                    const res = await apiCall('/ekonomia/api/favorite-currencies');
                    if (!res.ok) return [];
                    const data = await res.json();
                    const favs = data.favorite_currencies || [];
                    reorderCurrenciesToTop(favs, availableCurrenciesCache);
                    return favs;
                } catch (e) {
                    console.warn('Failed to fetch favorite currencies', e);
                    return [];
                }
            }

            // Move selected currencies to top with formatted display
            function reorderCurrenciesToTop(favs, availableCurrencies) {
                console.log('Reordering currencies to top with favorites:', favs, availableCurrencies);
                if (!favs || favs.length === 0) return;

                // Create a map for quick lookup: code -> rate
                const rateMap = {};
                availableCurrencies.forEach(curr => {
                    rateMap[curr.code] = curr.rate;
                });

                console.log('Reordering favorites:', favs);
                console.log('Available rates:', rateMap);

                // Get the currency-item containers (not boxes themselves)
                const items = Array.from(container.querySelectorAll('.currency-item'));
                
                // Update the first 3 items with favorite currencies
                favs.forEach((favCurrency, index) => {
                    if (index < 3 && items[index]) {
                        const rate = rateMap[favCurrency.currency_code] || 0;
                        const box = items[index].querySelector('.currency-box');
                        
                        if (box) {
                            // Find and update only the text content, preserve all HTML structure
                            const titleElem = box.querySelector('.currency-title');
                            const valueElem = box.querySelector('.currency-value');
                            
                            if (titleElem) {
                                titleElem.textContent = `${favCurrency.currency_code} na PLN`;
                            }
                            
                            if (valueElem) {
                                valueElem.textContent = `${rate.toFixed(2)} zł`;
                            }
                            
                            // Update data-currency attribute
                            box.dataset.currency = favCurrency.currency_code;
                        }
                    }
                });
            }

            // Create modal for selecting favorites
            function createFavoritesModal() {
                const modal = document.createElement('div');
                modal.id = 'favoritesModal';
                modal.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0,0,0,0.5);
                    display: none;
                    z-index: 1000;
                    align-items: center;
                    justify-content: center;
                `;

                modal.innerHTML = `
                    <div style="background: white; padding: 30px; border-radius: 12px; max-width: 400px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">
                        <h3 style="margin-top: 0; color: #2B370A;">Wybierz do 3 ulubionych walut</h3>
                        <div id="favoritesCheckboxes" style="max-height: 300px; overflow-y: auto; margin: 20px 0;"></div>
                        <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 20px;">
                            <button id="closeFavModal" style="padding: 8px 16px; background: #ddd; border: none; border-radius: 6px; cursor: pointer;">Anuluj</button>
                            <button id="saveFavModal" style="padding: 8px 16px; background: #7E9E45; color: white; border: none; border-radius: 6px; cursor: pointer;">Zapisz</button>
                        </div>
                    </div>
                `;

                document.body.appendChild(modal);
                return modal;
            }

            const modal = createFavoritesModal();

            // Show modal on currency-box click
            currencyBoxes.forEach(box => {
                box.style.cursor = 'pointer';
                box.addEventListener('click', async function(e) {
                    e.stopPropagation();
                    console.log('Currency box clicked:', this.dataset.currency);
                    
                    // Populate checkboxes
                    const checkboxContainer = document.getElementById('favoritesCheckboxes');
                    checkboxContainer.innerHTML = 'Ładowanie walut...';

                    // Get available currencies and current favorites
                    try {
                        // Load available currencies if not cached
                        if (availableCurrenciesCache.length === 0) {
                            availableCurrenciesCache = await loadAvailableCurrencies();
                        }

                        const favRes = await apiCall('/ekonomia/api/favorite-currencies');
                        const favData = favRes.ok ? await favRes.json() : { favorite_currencies: [] };
                        
                        const availableCurrencies = availableCurrenciesCache;
                        const selectedCodes = favData.favorite_currencies.map(f => f.currency_code);

                        // Create checkboxes for available currencies
                        checkboxContainer.innerHTML = '';
                        availableCurrencies.forEach(curr => {
                            const code = curr.code;
                            const rate = curr.rate;
                            
                            const label = document.createElement('label');
                            label.style.cssText = 'display: flex; align-items: center; margin: 10px 0; cursor: pointer; font-size: 14px;';
                            
                            const checkbox = document.createElement('input');
                            checkbox.type = 'checkbox';
                            checkbox.value = code;
                            checkbox.checked = selectedCodes.includes(code);
                            checkbox.style.marginRight = '10px';
                            checkbox.style.cursor = 'pointer';
                            checkbox.style.width = '18px';
                            checkbox.style.height = '18px';

                            // Limit to 3 selections
                            checkbox.addEventListener('change', function() {
                                const checked = document.querySelectorAll('#favoritesCheckboxes input:checked');
                                if (checked.length > 3) {
                                    this.checked = false;
                                    alert('Możesz wybrać maksymalnie 3 waluty');
                                }
                            });

                            label.appendChild(checkbox);
                            const textNode = document.createTextNode(code);
                            label.appendChild(textNode);
                            checkboxContainer.appendChild(label);
                        });

                        // Show modal
                        modal.style.display = 'flex';
                        console.log('Modal displayed with', availableCurrencies.length, 'currencies');
                    } catch (err) {
                        console.error('Error populating modal:', err);
                        checkboxContainer.innerHTML = '<div style="color: red;">Błąd przy ładowaniu walut</div>';
                    }
                });
            });

            // Close modal on background click
            modal.addEventListener('click', function(e) {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });

            // Close modal
            document.getElementById('closeFavModal').addEventListener('click', () => {
                modal.style.display = 'none';
            });

            // Save favorites
            document.getElementById('saveFavModal').addEventListener('click', async () => {
                const checked = Array.from(document.querySelectorAll('#favoritesCheckboxes input:checked')).map(cb => cb.value);
                
                try {
                    // Get current favorites
                    const res = await apiCall('/ekonomia/api/favorite-currencies');
                    const data = res.ok ? await res.json() : { favorite_currencies: [] };
                    const currentCodes = data.favorite_currencies.map(f => f.currency_code);

                    // Delete removed ones
                    for (const code of currentCodes) {
                        if (!checked.includes(code)) {
                            await apiCall(`/ekonomia/api/favorite-currencies/${code}`, {
                                method: 'DELETE'
                            });
                        }
                    }

                    // Add new ones
                    for (const code of checked) {
                        if (!currentCodes.includes(code)) {
                            await apiCall('/ekonomia/api/favorite-currencies', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ currency_code: code })
                            });
                        }
                    }

                    // Reload favorites
                    loadFavorites();
                    modal.style.display = 'none';
                } catch (err) {
                    console.error('Error saving favorites:', err);
                    alert('Błąd przy zapisywaniu ulubionych');
                }
            });

            // Load on page load
            (async () => {
                // Pre-load available currencies cache
                if (availableCurrenciesCache.length === 0) {
                    availableCurrenciesCache = await loadAvailableCurrencies();
                }
                loadFavorites();
            })();
        }

        // Start initialization
        initFavoritesSetup();
    }


    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", function () {
            init();
            setupChartLoader();
            setupFavoriteCurrency();
        });
    } else {
        init();
        setupChartLoader();
        setupFavoriteCurrency();
    }
})();
