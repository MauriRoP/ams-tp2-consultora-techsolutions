# Consultora Tech Solutions - Slice 1 (Demo MVP)

Trabajo práctico  **Análisis y Metodología de Sistemas** (Instituto Da Vinci).

## Stack Técnico
- **Backend:** Python 3 + Flask
- **Persistencia:** SQLite + Flask-SQLAlchemy
- **Frontend / Vistas:** Jinja2 + Bootstrap 5

## Pasos de Instalación y Ejecución Local

1. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate

   *Instalar dependencias:
   pip install -r requirements.txt

   *Inicializar la base de datos con datos semilla (Seed Data):
   flask --app app.py init-db

   *Ejecutar el servidor local:
   flask --app app.py run --port 5000

   -Acceder desde el navegador a: http://127.0.0.1:5000



   