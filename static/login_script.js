// Handle login form submission
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // Get username from form and store in sessionStorage
            const username = document.getElementById('username').value;
            sessionStorage.setItem('username', username);
            
            // Get form data
            const formData = new FormData(loginForm);
            
            // Submit to backend
            fetch('/login', {
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
                    // Error response - try to get JSON error message
                    try {
                        const data = await response.json();
                        alert('Error: ' + (data.error || 'Login failed'));
                        return;
                    } catch (e) {
                        // Not JSON, show generic error
                        alert('Error: Login failed. Please try again.');
                        return;
                    }
                }
                
                // Check the final URL to determine if login was successful
                // Success: Flask redirects to '/' (dashboard)
                // Failure: Flask redirects to '/login' (login page)
                const finalUrl = new URL(response.url);
                if (finalUrl.pathname === '/login') {
                    // Still on login page - login failed
                    alert('Error: Invalid credentials');
                    return;
                } else {
                    // Redirected to dashboard - login succeeded
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                alert('Error: An error occurred during login. Please try again.');
            });
        });
    }
});