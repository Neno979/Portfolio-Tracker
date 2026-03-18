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