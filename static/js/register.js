
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    
    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ name, email, password })
                });

                const data = await response.json();
                console.log(data);                

                if (response.ok) {
                    alert('¡Registro exitoso! Ahora serás redirigido para iniciar sesión.');
                    window.location.href = '/login';
                } else {
                    alert(`Error: ${data.error}`);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Ocurrió un error en la conexión.');
            }
        });
    }
});