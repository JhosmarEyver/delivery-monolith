FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# # Imagen base liviana
# FROM python:3.11-slim

# # Evitar que Python escriba archivos .pyc y forzar salida de logs sin buffer
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# # Directorio de trabajo en el contenedor
# WORKDIR /app

# # Instalar dependencias del sistema operativo (necesarias para PostgreSQL driver)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libpq-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copiar e instalar dependencias de Python
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# # Copiar el código fuente
# COPY ./src ./src

# # Exponer el puerto del servidor
# EXPOSE 8000

# # Comando para ejecutar la aplicación con Uvicorn
# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
