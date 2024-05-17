
FROM python:3.8-slim

# Set the working directory inside the container
WORKDIR /main

# Copy the requirements.txt file into the container at /app
COPY requirements.txt .

# Install any dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container at /app
COPY . .


EXPOSE 30001


CMD ["python", "main.py"]