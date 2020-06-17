# Python Image
FROM python:3.7.7-buster
ARG ver=main
WORKDIR /app

# Copy source into container
COPY . .

# Install requirements
RUN apt update && apt -y install libffi-dev python3.7-dev && \
    if [ "$ver" = "dev" ] ; then pip install \
    git+https://github.com/Rapptz/discord.py.git#egg=discord.py[voice] ; \
    else pip install discord.py[voice]  ; fi && \
    pip install -r requirements.txt && \
    pip install -r sharding-requirements.txt && \
    pip install uvloop

# Run
CMD ["python", "-u", "./heleus.py", "--uvloop"]
