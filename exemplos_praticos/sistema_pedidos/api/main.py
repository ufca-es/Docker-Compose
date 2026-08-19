"""API do sistema de pedidos.

Cria pedidos no PostgreSQL e publica a tarefa de processamento no Redis
somente depois que a transacao for confirmada, evitando anunciar um
pedido que nao foi persistido.
"""

import logging
import os
import threading
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from typing import Optional

import psycopg2
import psycopg2.extras
from psycopg2 import pool as pg_pool
import redis
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("api")

DATABASE_HOST = os.environ["DATABASE_HOST"]
DATABASE_PORT = int(os.environ.get("DATABASE_PORT", "5432"))
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))

FILA_PEDIDOS = "fila:pedidos"

MAX_TENTATIVAS_CONEXAO = 5
INTERVALO_TENTATIVA_SEGUNDOS = 2


class ErroPostgresIndisponivel(RuntimeError):
    pass


class ErroRedisIndisponivel(RuntimeError):
    pass


def _parametros_postgres() -> dict:
    return dict(
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        connect_timeout=5,
    )


def _conectar_postgres():
    return psycopg2.connect(**_parametros_postgres())


def _criar_pool_postgres() -> pg_pool.ThreadedConnectionPool:
    return pg_pool.ThreadedConnectionPool(1, 10, **_parametros_postgres())


def _criar_cliente_redis() -> redis.Redis:
    cliente = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        socket_connect_timeout=5,
        socket_timeout=5,
        decode_responses=True,
    )
    cliente.ping()
    return cliente


_pool_lock = threading.Lock()
_pool: Optional[pg_pool.ThreadedConnectionPool] = None

_redis_lock = threading.Lock()
_redis_client: Optional[redis.Redis] = None


def _obter_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is not None:
            return _pool
        ultimo_erro: Optional[Exception] = None
        for tentativa in range(1, MAX_TENTATIVAS_CONEXAO + 1):
            try:
                _pool = _criar_pool_postgres()
                logger.info("Conectado ao PostgreSQL em %s:%s", DATABASE_HOST, DATABASE_PORT)
                return _pool
            except psycopg2.OperationalError as erro:
                ultimo_erro = erro
                logger.warning(
                    "Falha ao conectar ao PostgreSQL (tentativa %s/%s): %s",
                    tentativa, MAX_TENTATIVAS_CONEXAO, erro,
                )
                if tentativa < MAX_TENTATIVAS_CONEXAO:
                    time.sleep(INTERVALO_TENTATIVA_SEGUNDOS)
        raise ErroPostgresIndisponivel(str(ultimo_erro))


def obter_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    with _redis_lock:
        if _redis_client is not None:
            return _redis_client
        ultimo_erro: Optional[Exception] = None
        for tentativa in range(1, MAX_TENTATIVAS_CONEXAO + 1):
            try:
                _redis_client = _criar_cliente_redis()
                logger.info("Conectado ao Redis em %s:%s", REDIS_HOST, REDIS_PORT)
                return _redis_client
            except redis.RedisError as erro:
                ultimo_erro = erro
                logger.warning(
                    "Falha ao conectar ao Redis (tentativa %s/%s): %s",
                    tentativa, MAX_TENTATIVAS_CONEXAO, erro,
                )
                if tentativa < MAX_TENTATIVAS_CONEXAO:
                    time.sleep(INTERVALO_TENTATIVA_SEGUNDOS)
        raise ErroRedisIndisponivel(str(ultimo_erro))


@contextmanager
def conexao_postgres():
    pool = _obter_pool()
    conn = pool.getconn()
    quebrada = False
    try:
        yield conn
    except psycopg2.OperationalError as erro:
        quebrada = True
        raise ErroPostgresIndisponivel(str(erro)) from erro
    finally:
        if quebrada:
            pool.putconn(conn, close=True)
        else:
            try:
                conn.rollback()
            except Exception:
                pass
            pool.putconn(conn)


def publicar_na_fila(pedido_id: int) -> None:
    global _redis_client
    cliente = obter_redis()
    try:
        cliente.lpush(FILA_PEDIDOS, str(pedido_id))
    except redis.RedisError as erro:
        _redis_client = None
        raise ErroRedisIndisponivel(str(erro)) from erro


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        _obter_pool()
    except ErroPostgresIndisponivel as erro:
        logger.error("PostgreSQL indisponivel na inicializacao: %s", erro)
    try:
        obter_redis()
    except ErroRedisIndisponivel as erro:
        logger.error("Redis indisponivel na inicializacao: %s", erro)
    yield


app = FastAPI(title="Sistema de pedidos - API", lifespan=lifespan)


@app.exception_handler(ErroPostgresIndisponivel)
async def _tratar_erro_postgres(request: Request, exc: ErroPostgresIndisponivel):
    return JSONResponse(status_code=503, content={"detail": f"PostgreSQL indisponivel: {exc}"})


@app.exception_handler(ErroRedisIndisponivel)
async def _tratar_erro_redis(request: Request, exc: ErroRedisIndisponivel):
    return JSONResponse(status_code=503, content={"detail": f"Redis indisponivel: {exc}"})


class PedidoCriar(BaseModel):
    cliente: str = Field(min_length=1, max_length=120)
    descricao: str = Field(min_length=1)


class Pedido(BaseModel):
    id: int
    cliente: str
    descricao: str
    status: str
    criado_em: datetime
    processado_em: Optional[datetime] = None


COLUNAS_PEDIDO = "id, cliente, descricao, status, criado_em, processado_em"


@app.post("/pedidos", response_model=Pedido, status_code=201)
def criar_pedido(dados: PedidoCriar):
    with conexao_postgres() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"""
                INSERT INTO pedidos (cliente, descricao)
                VALUES (%s, %s)
                RETURNING {COLUNAS_PEDIDO}
                """,
                (dados.cliente, dados.descricao),
            )
            pedido = cur.fetchone()
        conn.commit()

    publicar_na_fila(pedido["id"])
    return pedido


@app.get("/pedidos", response_model=list[Pedido])
def listar_pedidos():
    with conexao_postgres() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(f"SELECT {COLUNAS_PEDIDO} FROM pedidos ORDER BY id")
            return cur.fetchall()


@app.get("/pedidos/{pedido_id}", response_model=Pedido)
def obter_pedido(pedido_id: int):
    with conexao_postgres() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                f"SELECT {COLUNAS_PEDIDO} FROM pedidos WHERE id = %s",
                (pedido_id,),
            )
            pedido = cur.fetchone()
    if pedido is None:
        raise HTTPException(status_code=404, detail="Pedido nao encontrado")
    return pedido


@app.get("/health")
def verificar_saude():
    dependencias = {}
    saudavel = True

    try:
        conn = _conectar_postgres()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            conn.close()
        dependencias["postgres"] = "ok"
    except Exception as erro:
        saudavel = False
        dependencias["postgres"] = f"erro: {erro}"

    try:
        _criar_cliente_redis().close()
        dependencias["redis"] = "ok"
    except Exception as erro:
        saudavel = False
        dependencias["redis"] = f"erro: {erro}"

    corpo = {"status": "ok" if saudavel else "erro", "dependencias": dependencias}
    if not saudavel:
        return JSONResponse(status_code=503, content=corpo)
    return corpo
