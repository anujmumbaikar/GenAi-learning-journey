FROM mcr.microsoft.com/devcontainers/python:3.12

ENV PYTHONUNBUFFERED=1

RUN sudo apt-get update && \
    sudo apt-get install -y curl

RUN pip install --upgrade pip

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH=/root/.local/bin:$PATH
WORKDIR /workspaces/${localWorkspaceFolderBasename}
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

