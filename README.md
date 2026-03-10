# Claude Code Sample Repository

このリポジトリはClaude Codeを使用するためのサンプルプロジェクトです。
生成AI APIは基盤技術Tが配備したAWSのbedrockを利用します。

## Claude Codeについて

Claude CodeはAnthropic社が提供するAIアシスタント「Claude」のCLIツールです。コードの作成、編集、デバッグ、リファクタリングなど、様々なプログラミングタスクを支援します。

## 使い方

1. このリポジトリをクローン
2. .env.sampleを.envに名前変更して、各環境変数に必要な情報を入力
3. devcontainer.jsonにて2箇所の<your-name>を自分の名前に変更
4. devcontainerを展開（VSCodeでreopen in container）
5. ターミナルに"claude"を入力（claude codeを展開）

## 機能

- コード生成と編集
- バグ修正とデバッグ支援
- リファクタリング
- テスト作成
- ドキュメント生成

## ENEOS社内LAN経由での接続について

※この機能が特に不要で、かつ”Unable to connect to API (ConnectionRefused)”というエラーが出る場合は、「"containerEnv": {"no_proxy": ~~~~~~},」の部分を削除すればClaudeCodeは問題無く使用できる
devcontainer.json内の"containerEnv"にてBedrockに対してno_proxy設定をしており、
外部インターネットを経由しない閉域ルート（社内LAN->DirectConnect->Bedrock）での接続が可能です。
適切に接続されているかは以下コマンドで確認。

```
echo $no_proxy
```
bedrock.ap-northeast-1.amazonaws.com,bedrock-runtime.ap-northeast-1.amazonaws.com
```
curl -v https://bedrock-runtime.ap-northeast-1.amazonaws.com
```
* Uses proxy env variable no_proxy == 'bedrock.ap-northeast-1.amazonaws.com,bedrock-runtime.ap-northeast-1.amazonaws.com'
*   Trying 10.81.16.181:443...
* Connected to bedrock-runtime.ap-northeast-1.amazonaws.com (10.81.16.181) port 443 (#0)


## 参考リンク

- [Claude Code 公式ドキュメント](https://code.claude.com/docs/ja/overview)
- [AWS Bedrock 対応モデル一覧](https://docs.aws.amazon.com/ja_jp/bedrock/latest/userguide/inference-profiles-support.html)
※プロンプトデータを国内に留めておきたい特別な事情が無い限り、"global.~~"のモデルでok
