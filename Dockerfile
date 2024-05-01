FROM python:3.8

# Install necessary system packages
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    tesseract-ocr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Install NVIDIA packages
RUN distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list \
    && apt-get update && apt-get install -y nvidia-container-toolkit \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Set the default command to execute when the container starts
CMD [ "python", "your_script.py" ]
