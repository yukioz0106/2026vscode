import os
import json
import base64
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g
import anthropic

app = Flask(__name__)
DATABASE = 'assets.db'

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS fixed_assets (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_name          TEXT    NOT NULL,
                asset_category      TEXT,
                acquisition_date    TEXT,
                acquisition_cost    INTEGER,
                useful_life         INTEGER,
                depreciation_method TEXT,
                vendor_name         TEXT,
                invoice_number      TEXT,
                notes               TEXT,
                created_at          TEXT
            )
        ''')
        db.commit()


# ---------------------------------------------------------------------------
# Claude API: invoice analysis
# ---------------------------------------------------------------------------

def analyze_invoice_with_claude(file_bytes: bytes, file_type: str) -> dict:
    """Send invoice file to Claude and extract fixed-asset registration data."""
    client = anthropic.Anthropic()

    b64_data = base64.standard_b64encode(file_bytes).decode('utf-8')

    # Normalise jpeg alias
    if file_type == 'image/jpg':
        file_type = 'image/jpeg'

    image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

    if file_type in image_types:
        content_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": file_type, "data": b64_data},
        }
    else:  # PDF
        content_block = {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64_data},
        }

    prompt = (
        "この請求書から固定資産登録に必要な情報を抽出してください。\n"
        "以下のJSON形式のみで回答し、余分なテキストは一切含めないでください。\n"
        "情報が見つからない場合は null を使用してください。\n\n"
        "{\n"
        '  "asset_name": "資産名称（品目・商品名・サービス名）",\n'
        '  "asset_category": "資産区分（建物/構築物/機械装置/車両運搬具/工具器具備品/ソフトウエア/その他 から選択）",\n'
        '  "acquisition_date": "取得日（YYYY-MM-DD形式、請求日や発行日を使用）",\n'
        '  "acquisition_cost": 取得価額（円単位の整数、税込合計金額）,\n'
        '  "useful_life": 法定耐用年数（整数、不明はnull）,\n'
        '  "depreciation_method": "償却方法（定額法 または 定率法）",\n'
        '  "vendor_name": "取引先名（請求元の会社名または個人名）",\n'
        '  "invoice_number": "請求書番号・伝票番号",\n'
        '  "notes": "備考（品番・仕様・数量など補足情報）"\n'
        '}'
    )

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                content_block,
                {"type": "text", "text": prompt},
            ],
        }],
    )

    result_text = response.content[0].text.strip()

    # Strip markdown fences if present
    if '```json' in result_text:
        result_text = result_text.split('```json')[1].split('```')[0].strip()
    elif '```' in result_text:
        result_text = result_text.split('```')[1].split('```')[0].strip()

    # Isolate the JSON object
    start = result_text.find('{')
    end = result_text.rfind('}') + 1
    if start >= 0 and end > start:
        result_text = result_text[start:end]

    return json.loads(result_text)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'error': 'ファイルが選択されていません'}), 400

    ext_to_type = {
        '.pdf':  'application/pdf',
        '.jpg':  'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png':  'image/png',
        '.gif':  'image/gif',
        '.webp': 'image/webp',
    }
    fname = file.filename.lower()
    file_type = next((mime for ext, mime in ext_to_type.items() if fname.endswith(ext)), None)
    if not file_type:
        return jsonify({'error': 'PDF・JPEG・PNG・GIF・WebP ファイルのみ対応しています'}), 400

    file_bytes = file.read()
    if not file_bytes:
        return jsonify({'error': 'ファイルが空です'}), 400
    if len(file_bytes) > 10 * 1024 * 1024:
        return jsonify({'error': 'ファイルサイズが大きすぎます（10MB 以下にしてください）'}), 400

    try:
        data = analyze_invoice_with_claude(file_bytes, file_type)
        return jsonify({'success': True, 'data': data})
    except json.JSONDecodeError:
        return jsonify({'error': '請求書データの解析に失敗しました。別のファイルをお試しください。'}), 500
    except anthropic.AuthenticationError:
        return jsonify({'error': 'APIキーが無効です。ANTHROPIC_API_KEY 環境変数を確認してください。'}), 500
    except Exception as exc:
        return jsonify({'error': f'エラーが発生しました: {exc}'}), 500


@app.route('/api/assets', methods=['GET'])
def get_assets():
    rows = get_db().execute(
        'SELECT * FROM fixed_assets ORDER BY created_at DESC'
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/assets', methods=['POST'])
def create_asset():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'データがありません'}), 400
    if not data.get('asset_name', '').strip():
        return jsonify({'error': '資産名称は必須です'}), 400

    def to_int(v):
        try:
            return int(v) if v not in (None, '') else None
        except (ValueError, TypeError):
            return None

    db = get_db()
    cur = db.execute(
        '''INSERT INTO fixed_assets
               (asset_name, asset_category, acquisition_date, acquisition_cost,
                useful_life, depreciation_method, vendor_name, invoice_number,
                notes, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)''',
        (
            data.get('asset_name', '').strip(),
            data.get('asset_category') or None,
            data.get('acquisition_date') or None,
            to_int(data.get('acquisition_cost')),
            to_int(data.get('useful_life')),
            data.get('depreciation_method') or '定額法',
            data.get('vendor_name') or None,
            data.get('invoice_number') or None,
            data.get('notes') or None,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ),
    )
    db.commit()
    return jsonify({'success': True, 'id': cur.lastrowid})


@app.route('/api/assets/<int:asset_id>', methods=['DELETE'])
def delete_asset(asset_id):
    db = get_db()
    db.execute('DELETE FROM fixed_assets WHERE id = ?', (asset_id,))
    db.commit()
    return jsonify({'success': True})


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
