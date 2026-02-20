# Claude Code Sample Repository

このリポジトリはClaude Codeを使用するためのサンプルプロジェクトです。
生成AI APIは企画基盤Tが配備したAWSのbedrockを利用します。

## Claude Codeについて

Claude CodeはAnthropic社が提供するAIアシスタント「Claude」のCLIツールです。コードの作成、編集、デバッグ、リファクタリングなど、様々なプログラミングタスクを支援します。

## 使い方

1. このリポジトリをクローン
2. devcontainerを展開（VSCodeでreopen in container）
3. ターミナルにclaudeを入力（claude codeを展開）

## 機能

- コード生成と編集
- バグ修正とデバッグ支援
- リファクタリング
- テスト作成
- ドキュメント生成

## セットアップ

.env.sampleを参考に、企画基盤Tから配布される認証情報を入力
VSCodeからreopen in containerで展開（devcontainer）
claudeコマンドでclaude codeが展開される


```

## 参考リンク

- [Claude Code 公式ドキュメント](https://code.claude.com/docs/ja/overview)
- [AWS Bedrock 対応モデル一覧](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/inference-profiles-support.html?utm_source=chatgpt.com)
※プロンプトデータを国内に留めておきたい特別な事情が無い限り、"grobal.~~"のモデルでok