# Python Image
FROM python:3.7.7-buster
ARG ver=main
WORKDIR /app

# Copy source into container
COPY . .

# Install requirements
RUN apt update && apt -y install libffi-dev python3.7-dev && \
    pip install -r requirements.txt && \
    pip install uvloop

# Run
CMD ["python", "-u", "./heleus.py", "--uvloop"]
