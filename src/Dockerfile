# Pull base image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENV='PROD'

# Set work directory
WORKDIR /code

# Install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn python-dotenv

# Copy project
COPY . .

RUN ls -la /code

# Expose port 6000
EXPOSE 6000

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Command to run the application using the entrypoint script
CMD ["/entrypoint.sh"]