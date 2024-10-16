# Base CUDA image
FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

LABEL maintainer="breakstring@hotmail.com"
LABEL version="dev-20240209"
LABEL description="Docker image for GPT-SoVITS"


# Install 3rd party apps
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev parallel aria2 git git-lfs && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt initially to leverage Docker cache
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . /app

EXPOSE 9880

CMD ["python", "api.py"]

# docker build -t gpt-sovits .
# allocate gpu and 8gb memory
# docker run -d -p 9880:9880 --gpus all -m 8g gpt-sovits 