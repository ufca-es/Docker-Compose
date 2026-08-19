"""Worker do sistema de pedidos.

Consome tarefas da fila Redis ("fila:pedidos") publicadas pela API e
atualiza o estado do pedido no PostgreSQL: pendente -> processando ->
processado (ou falhou). Reconecta a cada dependencia com um numero
limitado de tentativas; se as tentativas se esgotarem, o processo
encerra e o Docker Compose (restart: unless-stopped) o reinicia.
"""

import logging
import os
import signal
import time
from datetime import datetime, timezone

import psycopg2
import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("worker")

DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = int(os.environ.get("DATABASE_PORT", "5432"))
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

FILA_PEDIDOS = "fila:pedidos"
BRPOP_TIMEOUT_SEGUNDOS = 5

MAX_TENTATIVAS_CONEXAO = 5
INTERVALO_TENTATIVA_SEGUNDOS = 2

_encerrar = False


def _tratar_sinal(signum, frame):
    global _encerrar
    logger.info("Sinal %s recebido, encerrando apos a tarefa atual...", signum)
    _encerrar = True


signal.signal(signal.SIGTERM, _tratar_sinal)
signal.signal(signal.SIGINT, _tratar_sinal)


def conectar_postgres():
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS_CONEXAO + 1):
        try:
            conn = psycopg2.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                dbname=POSTGRES_DB,
                user=POSTGRES_USER,
                password=POSTGRES_PASSWORD,
                connect_timeout=5,
            )
            conn.autocommit = False
            logger.info("Conectado ao PostgreSQL em %s:%s", DATABASE_HOST, DATABASE_PORT)
            return conn
        except psycopg2.OperationalError as erro:
            ultimo_erro = erro
            logger.warning(
                "Falha ao conectar ao PostgreSQL (tentativa %s/%s): %s",
                tentativa, MAX_TENTATIVAS_CONEXAO, erro,
            )
            if tentativa < MAX_TENTATIVAS_CONEXAO:
                time.sleep(INTERVALO_TENTATIVA_SEGUNDOS)
    logger.critical(
        "Nao foi possivel conectar ao PostgreSQL apos %s tentativas: %s",
        MAX_TENTATIVAS_CONEXAO, ultimo_erro,
    )
    raise SystemExit(1)


def conectar_redis():
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS_CONEXAO + 1):
        try:
            cliente = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                socket_connect_timeout=5,
                socket_timeout=None,
                decode_responses=True,
            )
            cliente.ping()
            logger.info("Conectado ao Redis em %s:%s", REDIS_HOST, REDIS_PORT)
            return cliente
        except redis.RedisError as erro:
            ultimo_erro = erro
            logger.warning(
                "Falha ao conectar ao Redis (tentativa %s/%s): %s",
                tentativa, MAX_TENTATIVAS_CONEXAO, erro,
            )
            if tentativa < MAX_TENTATIVAS_CONEXAO:
                time.sleep(INTERVALO_TENTATIVA_SEGUNDOS)
    logger.critical(
        "Nao foi possivel conectar ao Redis apos %s tentativas: %s",
        MAX_TENTATIVAS_CONEXAO, ultimo_erro,
    )
    raise SystemExit(1)


def _marcar_processando(conn, pedido_id: int) -> bool:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pedidos SET status = 'processando' "
            "WHERE id = %s AND status IN ('pendente', 'processando') "
            "RETURNING id",
            (pedido_id,),
        )
        atualizado = cur.fetchone() is not None
    conn.commit()
    return atualizado


def _marcar_processado(conn, pedido_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "UPDATE pedidos SET status = 'processado', processado_em = %s WHERE id = %s",
            (datetime.now(timezone.utc), pedido_id),
        )
    conn.commit()


def _marcar_falhou(conn, pedido_id: int) -> None:
    with conn.cursor() as cur:
        cur.execute("UPDATE pedidos SET status = 'falhou' WHERE id = %s", (pedido_id,))
    conn.commit()


def processar_pedido(conn, pedido_id: int) -> None:
    logger.info("Processando pedido %s", pedido_id)
    if not _marcar_processando(conn, pedido_id):
        logger.warning("Pedido %s nao esta pendente nem processando; ignorado", pedido_id)
        return

    try:
        time.sleep(1)  # placeholder para o processamento real do pedido
    except Exception as erro:
        logger.error("Falha ao processar pedido %s: %s", pedido_id, erro)
        _marcar_falhou(conn, pedido_id)
        return

    _marcar_processado(conn, pedido_id)
    logger.info("Pedido %s processado", pedido_id)


def main() -> None:
    logger.info("Worker iniciado. Aguardando pedidos na fila '%s'", FILA_PEDIDOS)
    conn = conectar_postgres()
    cliente_redis = conectar_redis()

    while not _encerrar:
        try:
            item = cliente_redis.brpop(FILA_PEDIDOS, timeout=BRPOP_TIMEOUT_SEGUNDOS)
        except redis.RedisError as erro:
            logger.warning("Conexao com o Redis perdida: %s. Reconectando...", erro)
            cliente_redis = conectar_redis()
            continue

        if item is None:
            continue  # timeout do BRPOP, apenas para permitir checar encerramento

        _, pedido_id_bruto = item
        try:
            pedido_id = int(pedido_id_bruto)
        except ValueError:
            logger.error("Mensagem invalida na fila: %r", pedido_id_bruto)
            continue

        try:
            processar_pedido(conn, pedido_id)
        except psycopg2.OperationalError as erro:
            logger.warning("Conexao com o PostgreSQL perdida: %s. Reconectando...", erro)
            try:
                conn.close()
            except Exception:
                pass
            conn = conectar_postgres()
            try:
                cliente_redis.lpush(FILA_PEDIDOS, pedido_id_bruto)
            except redis.RedisError as erro_redis:
                logger.error(
                    "Nao foi possivel devolver o pedido %s a fila: %s", pedido_id, erro_redis
                )

    logger.info("Encerrando worker...")
    conn.close()
    cliente_redis.close()


if __name__ == "__main__":
    main()
