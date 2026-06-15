# Use the official Python lightweight image
FROM python:3.11-slim

# Set system environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV=production

# Set application directory inside container
WORKDIR /app

# Install dependency files first to utilize Docker build cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all repository code files to the container
COPY . .

# Default container listening port (can be overridden by cloud PORT env vars)
EXPOSE 8000

# Execute startup command
CMD ["python", "run.py"]
