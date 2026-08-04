FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN python -m pip install --no-cache-dir .

ENTRYPOINT ["bughunter-one"]
CMD ["--help"]
