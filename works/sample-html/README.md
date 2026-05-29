# sample-html

Analytics Dashboard を nginx で配信する Docker コンテナです。

## クイックスタート（推奨）

データ修正後は `rebuild.sh` を使うと、コンテナの削除・ビルド・起動を一括で行えます。

```bash
# プロジェクトルートから実行
./sample-html/rebuild.sh

# sample-htmlディレクトリから実行
cd sample-html && ./rebuild.sh

# ポートを指定する場合
./sample-html/rebuild.sh 8080
```

起動後は `http://localhost:5705/` でアクセスできます。

## 手動での起動手順

### 1. イメージのビルド

```bash
# sample-htmlディレクトリで実行
docker build -t sample-html .
```

### 2. コンテナの起動

```bash
docker run -d --name sample-html-app -p 5705:80 sample-html
```

### 3. ブラウザでアクセス

```
http://localhost:5705/
```

## 停止・削除

```bash
# コンテナを停止
docker stop sample-html-app

# コンテナを削除
docker rm sample-html-app
```

## ファイル構成

```
sample-html/
├── Dockerfile
├── README.md
├── rebuild.sh        # 削除 → ビルド → 起動を一括実行
├── index.html        # ダッシュボード（トップ）
├── css/
│   └── common.css    # 共通スタイル
├── js/
│   └── common.js     # 共通スクリプト
└── pages/
    ├── analytics.html
    ├── customers.html
    ├── marketing.html
    ├── notifications.html
    ├── orders.html
    ├── reports.html
    ├── revenue.html
    └── settings.html
```
