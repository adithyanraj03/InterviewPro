// Flash message handling
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    setTimeout(function() {
        const flashMessages = document.querySelectorAll('.flash-message');
        flashMessages.forEach(function(message) {
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        });
    }, 5000);

    // Close flash message on click
    document.querySelectorAll('.close-flash').forEach(function(button) {
        button.addEventListener('click', function() {
            const message = button.parentElement;
            message.style.opacity = '0';
            setTimeout(() => message.remove(), 300);
        });
    });

    // Form validation and enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;

            requiredFields.forEach(function(field) {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                    
                    // Create or update error message
                    let errorMsg = field.nextElementSibling;
                    if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                        errorMsg = document.createElement('div');
                        errorMsg.classList.add('error-message');
                        field.parentNode.insertBefore(errorMsg, field.nextSibling);
                    }
                    errorMsg.textContent = 'This field is required';
                }
            });

            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});

// Smooth scrolling
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
}); 