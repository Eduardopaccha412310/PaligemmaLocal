# Usa una imagen base oficial de Python 3.10
FROM python:3.10-slim

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt en el directorio de trabajo
COPY requirements.txt requirements.txt

# Instala las dependencias especificadas en requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el contenido del directorio actual en el directorio de trabajo
COPY . .

# Exponer el puerto 5000 para la aplicación Flask
EXPOSE 5000

# Define el comando por defecto para ejecutar la aplicación
CMD ["python", "app/app.py"]