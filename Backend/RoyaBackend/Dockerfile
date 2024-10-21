# Backend/RoyaBackEnd/Dockerfile

# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock from the Backend directory into the container
COPY ../Pipfile ../Pipfile.lock* ./

# Install pipenv
RUN pip install pipenv

# Install the dependencies using pipenv and explicitly specify the Python version
RUN pipenv install --deploy --ignore-pipfile --python /usr/local/bin/python3.10

# Copy the rest of the application code from RoyaBackEnd directory
COPY . .

# Run the Django development server (or the commands provided in docker-compose.yml)
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
