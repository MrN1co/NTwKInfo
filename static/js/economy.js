(function() {
    // Pobierz dane z globalnej zmiennej ustawionej przez serwer
    const RATES = window.ECON_DATA ? window.ECON_DATA.currency_rates : {};

    const amountEl = document.getElementById('amount');
    const fromEl = document.getElementById('currency-from');
    const toEl = document.getElementById('currency-to');
    const resultEl = document.getElementById('result');

    // Sprawdź czy elementy istnieją
    if (!amountEl || !fromEl || !toEl || !resultEl) {
        console.warn('Economy calculator elements not found');
        return;
    }

    const PL_FORMATTER = new Intl.NumberFormat('pl-PL', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    const MAX_AMOUNT = 999999999999; // Maximum allowed amount

    function compute() {
        const raw = amountEl.value.trim();
        if (raw === '' || raw === '.') { 
            resultEl.value = ''; 
            return; 
        }

        const normalized = raw.replace(',', '.');
        const a = parseFloat(normalized);

        if (isNaN(a) || a > MAX_AMOUNT) { 
            resultEl.value = ''; 
            return; 
        }

        const from = fromEl.value || 'PLN';
        const to = toEl.value || 'PLN';

        const rateFrom = RATES[from] !== undefined ? RATES[from] : 1;
        const rateTo = RATES[to] !== undefined ? RATES[to] : 1;

        const inPln = a * rateFrom;
        const res = inPln / rateTo;

        // Round to 2 decimal places and format
        const rounded = Math.round(res * 100) / 100;
        resultEl.value = PL_FORMATTER.format(rounded);
    }

    function enforceTwoDecimals() {
        let raw = amountEl.value;
        if (!raw) return;

        // Remove any characters except digits and separators
        let s = raw.replace(/[^0-9.,]/g, '');

        // Normalize commas to dots for processing
        let normalized = s.replace(/,/g, '.');

        // Keep only the first dot, remove further dots
        const firstDot = normalized.indexOf('.');
        if (firstDot !== -1) {
            normalized = normalized.slice(0, firstDot + 1) + normalized.slice(firstDot + 1).replace(/\./g, '');
        }

        // Limit integer part to maximum value length
        const maxLength = MAX_AMOUNT.toString().length;
        if (normalized.indexOf('.') !== -1) {
            const [intPart, decPart = ''] = normalized.split('.');
            const limitedIntPart = intPart.slice(0, maxLength);
            const dec = decPart.slice(0, 2);
            normalized = limitedIntPart + (dec.length > 0 || normalized.endsWith('.') ? '.' + dec : '');
        } else {
            normalized = normalized.slice(0, maxLength);
        }

        // Check if value exceeds maximum
        const numValue = parseFloat(normalized);
        if (!isNaN(numValue) && numValue > MAX_AMOUNT) {
            normalized = MAX_AMOUNT.toString();
        }

        // Update the input value
        amountEl.value = normalized;
    }

    // Event listeners
    amountEl.addEventListener('input', function () { 
        enforceTwoDecimals(); 
        compute(); 
    });
    fromEl.addEventListener('change', compute);
    toEl.addEventListener('change', compute);

    // Optional: button to trigger compute for users who click it
    document.querySelectorAll('.calc-box .btn').forEach(btn => {
        btn.addEventListener('click', compute);
    });

    // Swap handler for the emoji
    const swapBtn = document.getElementById('swap-btn');
    if (swapBtn) {
        swapBtn.addEventListener('click', function() {
            const valFrom = fromEl.value;
            const valTo = toEl.value;

            // helper: ensure select contains option with given value
            function ensureOption(sel, val) {
                if (val === undefined || val === null || val === '') return;
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

    // Initial computation
    compute();
})();
