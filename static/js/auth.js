document.addEventListener('DOMContentLoaded', function() {
    // Theme toggle functionality
    const themeToggle = document.createElement('button');
    themeToggle.textContent = "Toggle Theme";
    themeToggle.classList.add('theme-toggle');
    
    // Append the button to the body or a specific container
    document.body.appendChild(themeToggle);

    // Check for saved theme preference
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.body.classList.add(savedTheme);
    } else {
        // Default theme is light
        document.body.classList.add('light-theme');
    }

    // Add event listener for theme toggle
    themeToggle.addEventListener('click', function() {
        // Toggle between light and dark themes
        if (document.body.classList.contains('light-theme')) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            localStorage.setItem('theme', 'light-theme');
        }
    });

    // Account type selection and other existing functionality
    const accountTypeCards = document.querySelectorAll('.account-type-card');
    const accountTypeInputs = document.querySelectorAll('input[name="account_type"]');
    
    // Set the first account type as selected by default if none are selected
    if (accountTypeInputs.length > 0 && !Array.from(accountTypeInputs).some(input => input.checked)) {
        accountTypeInputs[0].checked = true;
        accountTypeCards[0].classList.add('selected');
    }
    
    accountTypeCards.forEach(card => {
        const input = card.querySelector('input[type="radio"]');
        
        // Initial styling based on selection
        if (input.checked) {
            card.classList.add('selected');
            card.style.borderColor = 'var(--primary-color)';
            card.style.backgroundColor = 'rgba(78, 115, 223, 0.05)';
        }
        
        // Click handler for the cards
        card.addEventListener('click', function() {
            // Reset all cards
            accountTypeCards.forEach(c => {
                c.classList.remove('selected');
                c.style.borderColor = '#e9ecef';
                c.style.backgroundColor = 'white';
            });
            
            // Mark this card as selected
            input.checked = true;
            this.classList.add('selected');
            this.style.borderColor = 'var(--primary-color)';
            this.style.backgroundColor = 'rgba(78, 115, 223, 0.05)';
        });
    });
    
    // Password strength validation
    const passwordInput = document.getElementById('password');
    
    if (passwordInput) {
        passwordInput.addEventListener('input', function() {
            validatePassword(this.value);
        });
    }
    
    // Form validation
    const registrationForm = document.querySelector('form[action*="register"]');
    
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            let accountTypeSelected = false;
            
            // Check account type selection
            accountTypeInputs.forEach(input => {
                if (input.checked) {
                    accountTypeSelected = true;
                }
            });
            
            if (!accountTypeSelected) {
                e.preventDefault();
                alert('Please select an account type.');
                return false;
            }
            
            // Check if passwords match
            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match.');
                return false;
            }
            
            // Check if password is strong enough
            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long.');
                return false;
            }
        });
    }
    
    // Add glassmorphism effect to auth cards
    const authCard = document.querySelector('.auth-card');
    
    if (authCard) {
        authCard.addEventListener('mousemove', (e) => {
            const rect = authCard.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            // Update CSS variables for the glass effect
            authCard.style.setProperty('--x', `${x}px`);
            authCard.style.setProperty('--y', `${y}px`);
            
            // Create a slight shadow/highlight effect
            const shadowX = (x / rect.width - 0.5) * 20;
            const shadowY = (y / rect.height - 0.5) * 20;
            authCard.style.boxShadow = `0 10px 30px rgba(0, 0, 0, 0.1),
                ${shadowX}px ${shadowY}px 30px rgba(78, 115, 223, 0.1)`;
        });
        
        authCard.addEventListener('mouseleave', () => {
            // Reset the shadow when mouse leaves
            authCard.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.1)';
        });
    }
    
    // Login form animation
    const loginForm = document.querySelector('form[action*="login"]');
    
    if (loginForm) {
        const formFields = loginForm.querySelectorAll('.form-control, .form-check, .btn');
        
        formFields.forEach((field, index) => {
            field.style.opacity = 0;
            field.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                field.style.transition = 'all 0.5s ease';
                field.style.opacity = 1;
                field.style.transform = 'translateY(0)';
            }, 100 * (index + 1));
        });
    }
});

/**
 * Validates password strength
 * @param {string} password - The password to validate
 */
function validatePassword(password) {
    const passwordLength = password.length;
    let strength = 0;
    
    if (passwordLength >= 8) {
        strength += 1;
    }
    
    if (/[A-Z]/.test(password)) {
        strength += 1;
    }
    
    if (/[0-9]/.test(password)) {
        strength += 1;
    }
    
    if (/[^A-Za-z0-9]/.test(password)) {
        strength += 1;
    }
    
    // Visual feedback can be added here
    const passwordInput = document.getElementById('password');
    
    if (strength === 0) {
        passwordInput.style.borderColor = '#e74a3b';
    } else if (strength < 3) {
        passwordInput.style.borderColor = '#f6c23e';
    } else {
        passwordInput.style.borderColor = '#1cc88a';
    }
}
