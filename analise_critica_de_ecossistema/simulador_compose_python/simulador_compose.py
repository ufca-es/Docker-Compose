import json
import os
import sqlite3
import time
from pathlib import Path


BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "volume_dados"
DB_PATH = DATA_DIR / "postgres_simulado.db"

COMPOSE_SIMULADO = {
    "services": {
        "app": {
            "image": "python-app",
            "ports": ["5000:5000"],
            "environment": {
                "DB_HOST": "db",
                "DB_NAME": "compose_demo",
            },
            "depends_on": ["db"],
        },
        "db": {
            "image": "postgres:simulado",
            "volumes": ["volume_dados:/var/lib/postgresql/data"],
        },
    },
    "volumes": {
        "volume_dados": "persiste os dados mesmo apos parar os servicos",
    },
}


def imprimir_titulo(texto):
    print("\n" + "=" * 70)
    print(texto)
    print("=" * 70)


def simular_criacao_de_rede():
    imprimir_titulo("1. Criando rede interna do Compose")
    print("Rede criada: compose_default")
    print("Os servicos poderao se comunicar pelo nome, como 'app' e 'db'.")


def simular_variaveis_de_ambiente():
    imprimir_titulo("2. Configurando variaveis de ambiente da aplicacao")
    variaveis = COMPOSE_SIMULADO["services"]["app"]["environment"]

    for nome, valor in variaveis.items():
        os.environ[nome] = valor
        print(f"{nome}={valor}")


def iniciar_banco_simulado():
    imprimir_titulo("3. Iniciando servico db")
    DATA_DIR.mkdir(exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS acessos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servico TEXT NOT NULL,
            criado_em TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    connection.commit()
    connection.close()

    print("Servico db iniciado.")
    print("Volume montado em: ./volume_dados")
    print("Banco simulado pronto para receber conexoes.")


def iniciar_aplicacao_simulada():
    imprimir_titulo("4. Iniciando servico app")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")

    print(f"A aplicacao vai conectar no host '{db_host}'.")
    print(f"Nome do banco configurado: {db_name}")
    print("No Docker Compose real, 'db' seria resolvido pela rede interna.")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute("INSERT INTO acessos (servico) VALUES (?);", ("app",))
    cursor.execute("SELECT COUNT(*) FROM acessos;")
    total_acessos = cursor.fetchone()[0]
    connection.commit()
    connection.close()

    print("Aplicacao iniciou e gravou um acesso no banco.")
    print(f"Total de acessos persistidos no volume: {total_acessos}")


def mostrar_compose_simulado():
    imprimir_titulo("Arquivo compose.yaml representado em Python")
    print(json.dumps(COMPOSE_SIMULADO, indent=4, ensure_ascii=False))


def main():
    imprimir_titulo("Simulador de Docker Compose em Python")

    mostrar_compose_simulado()
    time.sleep(1)
    simular_criacao_de_rede()
    time.sleep(1)
    simular_variaveis_de_ambiente()
    time.sleep(1)
    iniciar_banco_simulado()
    time.sleep(1)
    iniciar_aplicacao_simulada()

    imprimir_titulo("Resumo da simulacao")
    print("Conceitos demonstrados:")
    print("- servicos: app e db")
    print("- depends_on: app depende do db")
    print("- rede interna: app acessa db pelo nome")
    print("- environment: configuracao por variaveis")
    print("- volume: dados persistidos na pasta volume_dados")
    print("\nExecute novamente para ver o contador aumentar.")


if __name__ == "__main__":
    main()
