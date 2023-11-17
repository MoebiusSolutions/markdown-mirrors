ARG BASE_DOCKER_REGISTRY=
ARG BASE_DOCKER_IMAGE=python:3.11
FROM ${BASE_DOCKER_REGISTRY}${BASE_DOCKER_IMAGE}

ENV PYTHON_HOME=/opt/app

# Install prereqs to python dependency pull
RUN install -o root -g root -m 0755 -d "$PYTHON_HOME" && \
    # The existence of this dir causes pipenv to install libs to a local dir
    install -o root -g root -m 0755 -d "$PYTHON_HOME/.venv" && \
    pip3 install pipenv
WORKDIR "$PYTHON_HOME"
COPY Pipfile .
COPY Pipfile.lock .

# Pull python dependencies
RUN pipenv install

# Load source code
COPY src/ ./src/

# Update PATH
#ENV PATH="$PYTHON_HOME/bin:${PATH}"

ENTRYPOINT [ "pipenv", "run", "python3", "/opt/app/src/main.py" ]
