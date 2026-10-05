# 📌 Configuração do VSCode para Python e Django

## 📌 1. Instalando e Configurando o Ambiente Virtual (`.venv`)

### 🔹 Criando um Ambiente Virtual
Abra o terminal no VSCode (`Ctrl + ~`) e execute:

```sh
python -m venv .venv
```

### 🔹 Ativando o Ambiente Virtual
- **Windows (PowerShell ou CMD)**:
  ```sh
  .venv\Scripts\activate
  ```
- **Linux/macOS**:
  ```sh
  source .venv/bin/activate
  ```

---

## 📌 2. Configurando VSCode para Carregar `.venv` Automaticamente
Abra as configurações (`Ctrl + Shift + P` → "Preferences: Open Settings (JSON)") e adicione:

```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true
}
```

Se estiver no Windows:
```json
{
    "python.defaultInterpreterPath": "${workspaceFolder}\\.venv\\Scripts\\python.exe"
}
```

---

## 📌 3. Configurando o Runserver do Django no VSCode

### 🔹 Configuração para Executar com `F5`
1️⃣ Abra o **VSCode** e pressione `Ctrl + Shift + P`.
2️⃣ Digite **"Debug: Open launch.json"** e escolha **"Python"**.
3️⃣ No arquivo `launch.json`, adicione:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django Runserver",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "0.0.0.0:8000"],
            "django": true,
            "justMyCode": true,
            "console": "integratedTerminal",
            "env": {
                "DJANGO_SETTINGS_MODULE": "meuprojeto.settings"
            }
        }
    ]
}
```

✅ Agora, pressione **F5** para iniciar o servidor Django no VSCode.

### 🔹 Executando o `runserver` Manualmente
Se quiser rodar sem depuração, use:
```sh
python manage.py runserver
```
Ou em outra porta:
```sh
python manage.py runserver 8080
```

---

## 📌 4. Compartilhando Extensões do VSCode

### 🔹 Exportando e Importando Lista de Extensões (Método Manual)
**📤 Exportar Extensões:**
```sh
code --list-extensions > extensions.txt
```
**📥 Importar Extensões no Novo VSCode:**
```sh
cat extensions.txt | xargs -n 1 code --install-extension
```
*(No Windows, use `Get-Content extensions.txt | ForEach-Object { code --install-extension $_ }`)*

ou

### 🔹 Criando um `extensions.json` para Equipes
Crie `.vscode/extensions.json` dentro do projeto:
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-toolsai.jupyter"
    ]
}
```
---

## 📌 5. Solução de Problemas Comuns

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError: No module named 'django'` | Ative o `.venv` e rode `pip install django` |
| `OSError: [Errno 48] Address already in use` | Tente `python manage.py runserver 8080` ou `kill -9 <PID>` |
| `Could not import settings 'meuprojeto.settings'` | Verifique se está na pasta correta e o nome do módulo está certo no `launch.json` |

---

🎯 **Agora seu VSCode está pronto para desenvolver com Python e Django!** 🚀
