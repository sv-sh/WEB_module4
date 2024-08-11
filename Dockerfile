# Base image Linux with Python
FROM python:3.10-slim

# Create environment variable for the app directory
ENV APP_HOME /my_app

# Set the working directory in the container
WORKDIR $APP_HOME

# Set dependencies in container
COPY pyproject.toml $APP_HOME/pyproject.toml
COPY poetry.lock $APP_HOME/poetry.lock

RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev --only main

# Copy other files into the working directory
COPY . .

# Create the directory for the storage volume if it doesn't exist
RUN mkdir -p storage

# Expose the port the application will run on
EXPOSE 3000

# Command to run the program inside the container
CMD ["python", "main.py"]
