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

## ENEOS社内LAN経由での接続について

devcontainer.json内の"containerEnv"にてBedrockに対してno_proxy設定をしており、
外部インターネットを経由しない閉域ルート（社内LAN->DirectConnect->Bedrock）での接続が可能です。
適切に接続されているかは以下コマンドで確認。

echo $no_proxy
```
bedrock.ap-northeast-1.amazonaws.com,bedrock-runtime.ap-northeast-1.amazonaws.com
```
curl -v https://bedrock-runtime.ap-northeast-1.amazonaws.com
```
* Uses proxy env variable no_proxy == 'bedrock.ap-northeast-1.amazonaws.com,bedrock-runtime.ap-northeast-1.amazonaws.com'
*   Trying 10.81.16.181:443...
* Connected to bedrock-runtime.ap-northeast-1.amazonaws.com (10.81.16.181) port 443 (#0)
```

## 参考リンク

- [Claude Code公式ドキュメント](https://docs.anthropic.com/en/docs/claude-code)
