# Python API Basic

## Installation

**VSCode Plugins**:

- **REST Client** by Huachao Mao  
  [Install here](https://marketplace.visualstudio.com/items?itemName=humao.rest-client)

- **Snippets** by Frank GP  
  [Install here](https://marketplace.visualstudio.com/items?itemName=frankgp.frankgp)

---

```sh
# Check Python version
python --version

# List installed packages
pip list

# Install Flask
pip install flask

# Run the application
python app.py

# List all installed packages in the current environment
pip freeze

# Save current dependencies to a requirements file
pip freeze > requirements.txt

# Install dependencies from the requirements file
pip install -r requirements.txt

# Uninstall Flask
pip uninstall flask

# Uninstall all packages in the environment
pip freeze | xargs pip uninstall -y

```

## Para crear un entorno virtual en Python, sigue estos pasos:

### 1. Instalar virtualenv (si no lo tienes instalado)

Aunque Python 3.3 y versiones posteriores incluyen el módulo venv de manera predeterminada, si prefieres usar virtualenv, puedes instalarlo mediante pip:

```sh
pip install virtualenv
```

### 2. Crear un entorno virtual

Para crear un entorno virtual, ejecuta el siguiente comando:
Usando venv (método recomendado en Python 3.3+):

```sh
python3 -m venv venv
python -m venv nombre_del_entorno
```

Usando virtualenv (si prefieres este método):

```sh
virtualenv venv
virtualenv nombre_del_entorno
virtualenv nombre_del_entorno
```

### 3. Activar el entorno virtual

```sh
source venv/bin/activate
nombre_del_entorno\Scripts\activate
```

### 4. Instalar las dependencias

```sh
pip install -r requirements.txt
pip install flask
```

### 5. Desactivar el entorno virtual

```sh
deactivate
```
