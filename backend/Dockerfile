FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY . /app
RUN useradd --uid 10001 --create-home bauradar && mkdir -p /var/lib/bauradar && chown bauradar /var/lib/bauradar
USER bauradar
ENV BAURADAR_DB=/var/lib/bauradar/users.sqlite
EXPOSE 8000
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-proxy-headers"]
