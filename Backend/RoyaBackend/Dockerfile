# Use a lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the Pipfile and Pipfile.lock from the Backend directory into the container
COPY ../Pipfile ../Pipfile.lock* ./

# Install pipenv, which will manage dependencies for the application
RUN pip install pipenv

# Install the dependencies using pipenv and specify the Python version
RUN pipenv install --deploy --ignore-pipfile --python /usr/local/bin/python3.10

# Copy the rest of the application code from the current directory into the container
COPY . .

# Run the Django development server
# Note: This command can be replaced with the appropriate command from docker-compose.yml if necessary
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
