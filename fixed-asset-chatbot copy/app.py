import os
from flask import Flask, request, jsonify, render_template, session
import anthropic
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fixed-asset-chatbot-secret')

SYSTEM_PROMPT = """あなたは経理・会計の専門家AIアシスタントです。特に固定資産会計に精通しており、以下のトピックについて正確かつ丁寧に回答します。

【専門領域】
- 固定資産の取得・登録（取得価額の判定、資産区分の選定）
- 法定耐用年数（器具備品、機械装置、建物、車両など）
- 減価償却の計算（定額法・定率法・生産高比例法）
- 少額減価償却資産（10万円未満・20万円未満・30万円未満の取扱い）
- 一括償却資産（20万円未満の3年均等償却）
- 中小企業の少額資産特例（30万円未満の即時償却）
- 資本的支出と修繕費の判定
- 固定資産の除却・売却・廃棄処理
- 減損会計
- リース資産の会計処理（ファイナンスリース・オペレーティングリース）
- 税務上の償却限度額と会計上の償却費の調整
- 固定資産税の概要

【回答スタイル】
- 日本の会計基準（J-GAAP）および税法（法人税法）に基づいて回答する
- 金額計算が必要な場合は具体的な計算式を示す
- 判断が難しいケースでは複数の観点から説明する
- 必要に応じて税理士・会計士への相談を勧める
- 親切で分かりやすい言葉で説明する

質問者は経理担当者や経営者を想定してください。"""

conversation_store: dict[str, list] = {}


@app.route('/')
def index():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or not data.get('message', '').strip():
        return jsonify({'error': 'メッセージを入力してください'}), 400

    session_id = data.get('session_id') or session.get('session_id', 'default')
    user_message = data['message'].strip()

    if session_id not in conversation_store:
        conversation_store[session_id] = []

    conversation_store[session_id].append({
        "role": "user",
        "content": user_message
    })

    try:
        client = anthropic.AnthropicBedrock()
        model = os.environ.get('ANTHROPIC_MODEL', 'anthropic.claude-opus-4-6')
        response = client.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=conversation_store[session_id],
        )
        assistant_message = response.content[0].text

        conversation_store[session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # 会話履歴が長くなりすぎないよう直近20往復に制限
        if len(conversation_store[session_id]) > 40:
            conversation_store[session_id] = conversation_store[session_id][-40:]

        return jsonify({'reply': assistant_message})

    except Exception as exc:
        return jsonify({'error': f'エラーが発生しました: {exc}'}), 500


@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json() or {}
    session_id = data.get('session_id') or session.get('session_id', 'default')
    conversation_store.pop(session_id, None)
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
