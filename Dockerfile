# Stage 1: Build the Go binary
FROM golang:1.20-alpine AS builder

# Set the working directory
WORKDIR /app

# Copy the xdcc-cli source code into the container
COPY xdcc-cli /app

# Install git and make
RUN apk add --no-cache git make

# Build the xdcc-cli binary using make
RUN make

# Stage 2: Set up the Python environment and run the Gradio app
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the compiled xdcc-cli binary from the builder
COPY --from=builder /app/bin/xdcc /usr/local/bin/xdcc-cli

# Install Gradio
RUN pip install gradio

# Copy the Gradio app script
COPY gradio_app.py /app/gradio_app.py

# Expose port 7860 for the Gradio app
EXPOSE 7860

# Set the default command to run the Gradio app
CMD ["python", "/app/gradio_app.py"]

