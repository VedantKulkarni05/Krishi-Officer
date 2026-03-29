# Use an official Python runtime as a parent image
FROM python:3.11-slim

#copy the requirements file into the container
COPY . /home/app

# Set the working directory in the container
WORKDIR /home/app

#to install all the dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

#production command to run the application
CMD ["gunicorn","--bind","0.0.0.0:8000","--timeout","180","app:app"]