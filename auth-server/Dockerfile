FROM python:3.13-alpine
WORKDIR /app
COPY server.py admin.py bootstrap-users.json ./
RUN mkdir -p /data && adduser -D -u 10001 auth && chown -R auth:auth /app /data
USER auth
EXPOSE 8787
CMD ["python", "server.py"]
