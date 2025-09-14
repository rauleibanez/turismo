document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    /*alert(data.message);*/
                    showToast(data.message, "success");
                    // Redirigir al usuario a la página principal después del login exitoso
                    window.location.href = '/';
                } else {
                    /*alert(data.message);*/
                    showToast(data.message, "error");
                }
            } catch (error) {
                console.error('Error:', error);
                /*alert('Ocurrió un error al intentar iniciar sesión. Por favor, inténtalo de nuevo.');*/
                showToast('Ocurrió un error al intentar iniciar sesión. Por favor, inténtalo de nuevo.', "error");
            }
        });
    }

    /* Mensajes emergentes tipo Toast */
    function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`; // aplica clase dinámica
    toast.textContent = message;

    const container = document.getElementById('toast-container');
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, duration);
    }

/* FIN */
});
