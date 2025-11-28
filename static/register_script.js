// Handle registration form submission
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // Get username from form and store in sessionStorage
            const username = document.getElementById('username').value;
            sessionStorage.setItem('username', username);
            
            // Get form data
            const formData = new FormData(registerForm);
            
            // Submit to backend
            fetch('/register', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'include', // Include cookies/session for Flask-Login
                redirect: 'follow' // Allow fetch to follow redirects
            })
            .then(async response => {
                // Check if it's an error status (4xx or 5xx)
                if (!response.ok) {
                    console.log('Response is not OK, trying to parse error');
                    // Error response - try to get JSON error message
                    try {
                        const data = await response.json();
                        console.log('Got JSON error:', data);
                        alert('Error: ' + (data.error || 'Registration failed'));
                        return;
                    } catch (e) {
                        console.log('Failed to parse JSON, got error:', e);
                        // Not JSON, show generic error
                        alert('Error: Registration failed. Please try again.');
                        return;
                    }
                }
                
                console.log('Response is OK, redirecting to dashboard');
                // If we get here, response is OK (200-299)
                // This means either:
                // 1. Redirect was followed and we got the dashboard HTML (success!)
                // 2. Some other successful response
                // In either case, redirect to dashboard
                window.location.href = '/';
            })
            .catch(error => {
                console.error('Registration error in catch block:', error);
                console.error('Error message:', error.message);
                console.error('Error stack:', error.stack);
                // On any error, try redirecting (user might have been created)
                // This handles cases where redirect causes issues
                window.location.href = '/';
            });
        });
    }
});

