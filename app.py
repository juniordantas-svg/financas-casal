<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        /* Reset básico */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body, html {
            height: 100%;
            background-color: #1f1f1f; /* fundo uniforme */
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .login-container {
            background-color: #2c2c2c; /* cor do cartão */
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(0,0,0,0.6);
            width: 320px;
            text-align: center;
        }

        .login-container img {
            width: 120px;
            margin-bottom: 20px;
        }

        .login-container h2 {
            color: #ffffff;
            margin-bottom: 20px;
        }

        .login-container input {
            width: 100%;
            padding: 12px;
            margin: 8px 0;
            border: none;
            border-radius: 6px;
            background-color: #3a3a3a;
            color: #ffffff;
            font-size: 16px;
        }

        .login-container input::placeholder {
            color: #bfbfbf;
        }

        .login-container button {
            width: 100%;
            padding: 12px;
            margin-top: 16px;
            border: none;
            border-radius: 6px;
            background-color: #ff6b6b; /* cor do botão */
            color: #fff;
            font-size: 16px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .login-container button:hover {
            background-color: #ff5252;
        }

        /* Mensagem de erro */
        .error {
            color: #ff4c4c;
            margin-top: 10px;
            font-size: 14px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <img src="logo.png" alt="Logo"> <!-- coloque sua logo aqui -->
        <h2>Login</h2>
        <input type="text" id="username" placeholder="Usuário">
        <input type="password" id="password" placeholder="Senha">
        <button onclick="login()">Entrar</button>
        <div class="error" id="errorMsg">Usuário ou senha incorretos</div>
    </div>

    <script>
        function login() {
            const user = document.getElementById('username').value;
            const pass = document.getElementById('password').value;
            const errorDiv = document.getElementById('errorMsg');

            // Aqui você pode validar com backend ou dados estáticos
            if(user === 'admin' && pass === '1234') {
                alert('Login realizado com sucesso!');
                errorDiv.style.display = 'none';
                // redirecionar ou abrir próxima página
            } else {
                errorDiv.style.display = 'block';
            }
        }

        // Permitir login ao pressionar Enter
        document.addEventListener('keydown', function(e) {
            if(e.key === 'Enter') {
                login();
            }
        });
    </script>
</body>
</html>
