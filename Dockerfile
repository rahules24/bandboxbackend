# Use official Python image
FROM python:3.12-slim

# Set environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /code/

# Run collectstatic during build (optional)
# RUN python manage.py collectstatic --noinput

# Entrypoint and CMD
COPY entrypoint.sh /code/entrypoint.sh
RUN chmod +x /code/entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]

# Default command
CMD ["gunicorn", "bbdBackend.wsgi:application", "--bind", "0.0.0.0:8000"]
