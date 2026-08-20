import os
import time

from flask import Flask, jsonify
import redis

app = Flask(__name__)

# O host "redis" é resolvido automaticamente pelo Docker Compose,
# pois é o nome do serviço definido no docker-compose.yml.
# Quando rodamos com "docker run" puro, esse valor precisa ser
# passado manualmente via variável de ambiente REDIS_HOST.
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))


def get_redis_connection(retries=10, delay=1):
    """Tenta conectar ao Redis, aguardando o serviço ficar disponível."""
    last_error = None
    for _ in range(retries):
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
            client.ping()
            return client
        except redis.exceptions.ConnectionError as error:
            last_error = error
            time.sleep(delay)
    raise last_error


cache = get_redis_connection()


@app.route("/")
def index():
    contador = cache.incr("hits")
    return jsonify(
        mensagem="Ola! Esta aplicacao Flask esta conectada ao Redis.",
        total_de_acessos=contador,
        redis_host=REDIS_HOST,
    )


@app.route("/health")
def health():
    return jsonify(status="ok")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
