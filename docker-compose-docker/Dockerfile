# Stage 1: Build the image with setup commands
FROM alpine:latest as setup

RUN apk add --no-cache curl \
    && curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh \
    && apk add --no-cache docker-compose

# Stage 2: Final image
FROM alpine:latest

# Copy the setup commands from the setup stage
COPY --from=setup /usr/local/bin/docker /usr/local/bin/docker
COPY --from=setup /usr/local/bin/docker-compose /usr/local/bin/docker-compose

# Optionally, add any additional dependencies needed for your setup

# Command to run the container
CMD ["echo", "Setup commands executed successfully"]
