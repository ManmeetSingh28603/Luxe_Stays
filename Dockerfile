# Step 1: Use an official Python runtime as a parent image
FROM ghcr.io/python:3.12-slim  # GitHub Container Registry

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Install system dependencies for Node.js and npm (required for Tailwind CSS)
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean

# Step 4: Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Install npm dependencies for Tailwind CSS
COPY package.json package-lock.json /app/
RUN npm install

# Step 6: Copy the rest of the project files into the container
COPY . /app/

# Step 7: Build Tailwind CSS (this will compile the styles)
RUN python manage.py tailwind build  # Build Tailwind CSS

# Step 8: Collect static files for Django
RUN python manage.py collectstatic --noinput

# Step 9: Set the environment variable for Django settings (use production settings)
ENV DJANGO_SETTINGS_MODULE=luxestays_project.settings.production

# Step 10: Expose the port that the app will run on
EXPOSE 8000

# Step 11: Run Gunicorn to serve the Django app
CMD ["gunicorn", "luxestays_project.wsgi:application", "--bind", "0.0.0.0:8000"]
