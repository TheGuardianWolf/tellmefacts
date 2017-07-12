# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory
WORKDIR /dummybot

# Copy the current directory contents into the container
ADD . /dummybot

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Run tests to verify build integrity
RUN python3 -m pytest tests

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app when the container launches
CMD ["python", "run_dummybot.py"]