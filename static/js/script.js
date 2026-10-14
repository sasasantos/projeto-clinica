document.addEventListener('DOMContentLoaded', function() {
  const loginForm = document.getElementById('loginForm');

  if (loginForm) {
    loginForm.addEventListener('submit', async function(event) {
      event.preventDefault();

      const usuario = document.getElementById('usuario').value;
      const senha = document.getElementById('senha').value;
      const mensagemErro = document.getElementById('mensagemErro');

      mensagemErro.textContent = '';

      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ usuario: usuario, senha: senha })
        });

        const data = await response.json();

        if (response.ok && data.sucesso) {
          window.location.href = data.redirect;
        } else {
          mensagemErro.textContent = data.mensagem || 'Usuário ou senha inválidos.';
        }
      } catch (error) {
        console.error('Erro na requisição:', error);
        mensagemErro.textContent = 'Erro ao conectar ao servidor.';
      }
    });
  }
});