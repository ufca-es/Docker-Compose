#!/usr/bin/env bash

set -u

faltando=0

for ferramenta in docker kompose kubectl minikube; do
    if command -v "$ferramenta" >/dev/null 2>&1; then
        printf '[OK]      %s\n' "$ferramenta"
    else
        printf '[FALTANDO] %s\n' "$ferramenta"
        faltando=1
    fi
done

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        printf '[OK]      Docker Engine está acessível.\n'
    else
        printf '[ATENÇÃO] Docker existe, mas o Engine não está acessível.\n'
        faltando=1
    fi
fi

if command -v kubectl >/dev/null 2>&1; then
    if kubectl cluster-info >/dev/null 2>&1; then
        printf '[OK]      kubectl está conectado a um cluster.\n'
    else
        printf '[ATENÇÃO] kubectl existe, mas não está conectado a um cluster.\n'
    fi
fi

if [ "$faltando" -eq 0 ]; then
    printf '\nFerramentas disponíveis. Inicie o Minikube antes da etapa Kubernetes.\n'
else
    printf '\nPrepare as ferramentas antes da apresentação. Consulte o roteiro.\n'
fi

exit "$faltando"
