# Use an official Python runtime as a parent image
FROM node:8-alpine

# Set the working directory to /app
WORKDIR /slack-mock-tester

# Copy the current directory contents into the container at /app
ADD . /slack-mock-tester

# Install any needed packages specified in requirements.txt
RUN npm install

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["npm", "test"]