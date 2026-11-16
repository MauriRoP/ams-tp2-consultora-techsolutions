# Consultora Tech Solutions - MVP (Slice 1)

Sistema web transaccional B2B para la gestión del ciclo de vida de contratos y solicitudes de infraestructura IT, desarrollado como Caso de Estudio 3 para la materia Análisis y Metodología de Sistemas (AMS).

El sistema permite a empresas clientes visualizar su plan contratado (Soporte Básico, Infraestructura Pro o Enterprise Cloud) y generar solicitudes de modificación de servicio. Del lado del administrador, permite gestionar estas solicitudes, aprobándolas para actualizar el contrato automáticamente o rechazándolas con feedback.

## 👥 Equipo de Trabajo
* **Mauricio Rocha** 
* **Miguel Rocha** 
* **Santi** 
* **Wilson**
* **Priscila** 

## 🚀 Tecnologías Utilizadas
* **Backend:** Python, Flask
* **Base de Datos:** SQLite, SQLAlchemy (ORM)
* **Frontend:** Jinja2, HTML5, Bootstrap 5

## ⚙️ Instalación y Despliegue Local
* **Abran Visual Studio**

1. Clonar el repositorio e ingresar a la carpeta:

   git clone https://github.com/MauriRoP/ams-tp2-consultora-techsolutions.git

   cd ams-tp2-consultora-techsolution

## 1 Crear y activar el entorno virtual:
* **python -m venv venv**
# En Windows:
* **venv\Scripts\activate**

## 2 Instalar las dependencias requeridas:
* **pip install Flask Flask-SQLAlchemy**

## 3 Inicializar la base de datos, crea las tablas y carga los datos semilla:
* **flask --app app.py init-db**

## 4 Levantar el servidor de desarrollo:
* **flask --app app.py run --port 5000**

## 5 Acceder en el navegador web a: 
* **http://127.0.0.1:5000/**

### ⚠️ Posibles Problemas de Instalación en Windows (Troubleshooting)

**1. Error "Python was not found" al crear el entorno virtual:**
Si Windows no reconoce el comando `python` por problemas con las variables de entorno (PATH) o la Microsoft Store, utilizar el Python Launcher en su lugar:

* **py -m venv venv**

(Nota: Si el error persiste, se recomienda descargar el instalador oficial desde python.org y asegurarse de marcar la casilla "Add Python to PATH" antes de instalar).

### 2. Error "DLL load failed" al inicializar la base de datos (Bloqueo de Antivirus):
Dado que el proyecto utiliza archivos .pyd de librerías recientes, el Control Inteligente de Aplicaciones o Windows Defender pueden bloquear el comando init-db. Para solucionarlo:

* **Abrir Seguridad de Windows > Historial de protección.**

* **Buscar la alerta de bloqueo reciente (Control de aplicaciones).**

* **Desplegar las opciones y seleccionar "Permitir en el dispositivo".**

* **Volver a ejecutar el comando flask --app app.py init-db.**
