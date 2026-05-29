#!/bin/bash
set -e

# ビルドするDockerイメージ名。変更する場合はここを修正する
IMAGE_NAME="sample-html"

# 起動・停止・削除対象のコンテナ名。変更する場合はここを修正する
CONTAINER_NAME="sample-html-app"

# デフォルトのホスト側ポート。引数で上書き可能（例: ./rebuild.sh 8080）
# コンテナ内部はnginxの80番ポート固定のため、変更するのはホスト側のみ
PORT="${1:-5705}"

echo "==> コンテナを停止・削除します..."
docker stop "$CONTAINER_NAME" 2>/dev/null && echo "    停止: $CONTAINER_NAME" || echo "    (起動中のコンテナなし)"
docker rm   "$CONTAINER_NAME" 2>/dev/null && echo "    削除: $CONTAINER_NAME" || echo "    (削除対象のコンテナなし)"

echo "==> イメージをビルドします..."
docker build -t "$IMAGE_NAME" "$(dirname "$0")"

echo "==> コンテナを起動します (port: $PORT)..."
docker run -d --name "$CONTAINER_NAME" -p "${PORT}:80" "$IMAGE_NAME"

echo ""
echo "✔ 起動完了: http://localhost:${PORT}/index.html"
