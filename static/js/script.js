//password text visibility button
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);

    if (input.type === "password") {
        input.type = "text";
        icon.className = "bi bi-eye-slash";
    } else {
        input.type = "password";
        icon.className = "bi bi-eye";
    }
}

//Auto-off flash messages after 3 seconds
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');

    alerts.forEach(function(alert) {
        setTimeout(function() {
            // Fade out
            alert.style.transition = 'opacity 0.3s';
            alert.style.opacity = '0';

            // Remove from DOM after fade
            setTimeout(function() {
                alert.remove();
            }, 300);
        }, 3000);
    });
});

// Add coin form: restore last used choice on buy/sell radio button
document.addEventListener("DOMContentLoaded", function () {
    const buyRadio = document.getElementById("radio_buy");
    const sellRadio = document.getElementById("radio_sell");

    if (buyRadio && sellRadio && !buyRadio.checked && !sellRadio.checked) {
        // only restore if neither is already checked server-side (i.e. this is just for the Add coin form, not edit)
        const lastChoice = localStorage.getItem("last_transaction_type") || "buy";
        (lastChoice === "sell" ? sellRadio : buyRadio).checked = true;
    }

    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function () {
            const selected = document.querySelector('input[name="transaction_type"]:checked');
            if (selected) {
                localStorage.setItem("last_transaction_type", selected.value);
            }
        });
    }
});