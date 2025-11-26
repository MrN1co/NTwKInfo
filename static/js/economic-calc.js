(function() {
    // run after DOM ready to ensure elements exist
    function init() {
        const RATES = (window.ECON_DATA && window.ECON_DATA.currency_rates) || {};

        const amountEl = document.getElementById('amount');
        const fromEl = document.getElementById('currency-from');
        const toEl = document.getElementById('currency-to');
        const resultEl = document.getElementById('result');

        // Formatowanie wyniku: zawsze 2 miejsca po przecinku (zaokrąglone)
        const PL_FORMATTER = new Intl.NumberFormat('pl-PL', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });

        function compute() {
            const raw = amountEl.value.trim();
            if (raw === '') { resultEl.value = ''; return; }

            const hasTrailingSep = /[.,]$/.test(raw);
            const normalized = raw.replace(',', '.');
            const a = parseFloat(normalized);

            if (isNaN(a)) { resultEl.value = ''; return; }

            const from = fromEl.value || 'PLN';
            const to = toEl.value || 'PLN';

            const rateFrom = RATES[from] !== undefined ? RATES[from] : 1;
            const rateTo = RATES[to] !== undefined ? RATES[to] : 1;

            const inPln = a * rateFrom;
            const res = inPln / rateTo;

            // zaokrąglij numerycznie do 2 miejsc przed formatowaniem
            const rounded = Math.round(res * 100) / 100;
            let formatted = PL_FORMATTER.format(rounded);
            if (hasTrailingSep) {
                // Only append a trailing comma when the formatted value has no decimal separator yet.
                if (!formatted.includes(',')) {
                    formatted = formatted + ',';
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
            let s = raw.replace(/[^0-9.,]/g, '');

            // normalize commas to dot for processing
            let normalized = s.replace(/,/g, '.');

            // keep only the first dot, remove further dots
            const firstDot = normalized.indexOf('.');
            if (firstDot !== -1) {
                normalized = normalized.slice(0, firstDot + 1) + normalized.slice(firstDot + 1).replace(/\./g, '');
            }

            // limit to two decimal places if dot present
            if (normalized.indexOf('.') !== -1) {
                const [intPart, decPart = ''] = normalized.split('.');
                const dec = decPart.slice(0, 2);
                // if user had trailing separator, keep a trailing dot to indicate they typed it
                normalized = intPart + (dec.length > 0 ? '.' + dec : (hadTrailingSep ? '.' : ''));
            }

            // Enforce total digits (integer + fractional) <= MAX_DIGITS
            // Remove extra digits from the end while preserving the dot.
            const digitsOnly = normalized.replace(/[^0-9]/g, '');
            if (digitsOnly.length > MAX_DIGITS) {
                let over = digitsOnly.length - MAX_DIGITS;
                // Remove last 'over' digit characters from normalized
                while (over > 0) {
                    let lastIndex = -1;
                    for (let i = normalized.length - 1; i >= 0; i--) {
                        if (/\d/.test(normalized[i])) { lastIndex = i; break; }
                    }
                    if (lastIndex === -1) break;
                    normalized = normalized.slice(0, lastIndex) + normalized.slice(lastIndex + 1);
                    over--;
                }
                // If result ends with a dot and it wasn't intended as trailing sep, keep it only if hadTrailingSep
                if (normalized.endsWith('.') && !hadTrailingSep) {
                    normalized = normalized.slice(0, -1);
                }
            }

            // Update the input value (uses dot as separator for consistency in parsing)
            amountEl.value = normalized;
        }

        if (amountEl) amountEl.addEventListener('input', function () { enforceTwoDecimals(); compute(); });
        if (fromEl) fromEl.addEventListener('change', compute);
        if (toEl) toEl.addEventListener('change', compute);

        // Optional: button to trigger compute for users who click it
        document.querySelectorAll('.calc-box .btn').forEach(btn => btn.addEventListener('click', compute));

        // swap handler
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

        compute();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
