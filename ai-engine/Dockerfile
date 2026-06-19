# 1. Base Image: Use a lightweight Python version
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the dependencies file first (for caching speed)
COPY requirements.txt .

# 4. Install dependencies (and fix the CPU-only PyTorch issue to save space)
# We use --no-cache-dir to keep the image small
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

# 5. Copy your source code into the container
COPY . .

# 6. Expose the port the API runs on
EXPOSE 8001

# 7. The command to run when the container starts
CMD ["uvicorn", "inference_service:app", "--host", "0.0.0.0", "--port", "8001"]