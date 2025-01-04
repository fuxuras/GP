FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir flask
RUN pip install --no-cache-dir numba

EXPOSE 5000

ENV FLASK_APP=server.py

CMD ["python", "server.py"]