#!/bin/bash
set -e

# Arranca el servidor Ollama en background
ollama serve &
OLLAMA_PID=$!

# Espera hasta que el servidor acepte conexiones
# Usamos `ollama list` en lugar de curl porque la imagen no tiene curl instalado
echo "[ollama] Waiting for server to start..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done
echo "[ollama] Server is ready"

# Descarga los modelos si no están ya en el volumen
# Los modelos quedan cacheados en /root/.ollama (volumen persistente),
# así que en reinicios posteriores este paso es casi instantáneo

echo "[ollama] Pulling sqlcoder:7b (text-to-SQL model)..."
ollama pull sqlcoder:7b

echo "[ollama] Pulling llama3.2:3b (natural language model)..."
ollama pull llama3.2:3b

echo "[ollama] All models ready"

# Mantiene el servidor corriendo
wait $OLLAMA_PID
