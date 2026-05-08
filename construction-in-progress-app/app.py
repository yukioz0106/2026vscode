import os
import json
import base64
import sqlite3
import csv
import io
from datetime import datetime
from flask import Flask, request, jsonify, render_template, g, Response
import anthropic

app = Flask(__name__)
DATABASE = 'construction.db'


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
            CREATE TABLE IF NOT EXISTS construction_entries (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name        TEXT    NOT NULL,
                project_code        TEXT,
                vendor_name         TEXT,
                invoice_number      TEXT,
                invoice_date        TEXT,
                amount              INTEGER,
                tax_amount          INTEGER,
                total_amount        INTEGER,
                cost_center         TEXT,
                wbs_element         TEXT,
                gl_account          TEXT    DEFAULT '1521000',
                posting_date        TEXT,
                description         TEXT,
                notes               TEXT,
                status              TEXT    DEFAULT '未転送',
                created_at          TEXT
            )
        ''')
        db.commit()


def analyze_invoice_with_claude(file_bytes: bytes, file_type: str) -> dict:
    client = anthropic.AnthropicBedrock()

    b64_data = base64.standard_b64encode(file_bytes).decode('utf-8')

    if file_type == 'image/jpg':
        file_type = 'image/jpeg'

    image_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

    if file_type in image_types:
        content_block = {
            "type": "image",
            "source": {"type": "base64", "media_type": file_type, "data": b64_data},
        }
    else:
        content_block = {
            "type": "document",
            "source": {"type": "base64", "media_type": "application/pdf", "data": b64_data},
        }

    prompt = (
        "この請求書から建設仮勘定の計上に必要な情報を抽出してください。\n"
        "以下のJSON形式のみで回答し、余分なテキストは一切含めないでください。\n"
        "情報が見つからない場合は null を使用してください。\n\n"
        "{\n"
        '  "project_name": "工事・プロジェクト名称（品目・工事名・サービス名）",\n'
        '  "vendor_name": "取引先名（請求元の会社名または個人名）",\n'
        '  "invoice_number": "請求書番号・伝票番号",\n'
        '  "invoice_date": "請求日・発行日（YYYY-MM-DD形式）",\n'
        '  "amount": 税抜金額（円単位の整数）,\n'
        '  "tax_amount": 消費税額（円単位の整数）,\n'
        '  "total_amount": 税込合計金額（円単位の整数）,\n'
        '  "description": "摘要・品目の概要（50文字以内）",\n'
        '  "notes": "備考（品番・仕様・数量など補足情報）"\n'
        '}'
    )

    model = os.environ.get('ANTHROPIC_MODEL', 'anthropic.claude-opus-4-6')
    response = client.messages.create(
        model=model,
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

    if '```json' in result_text:
        result_text = result_text.split('```json')[1].split('```')[0].strip()
    elif '```' in result_text:
        result_text = result_text.split('```')[1].split('```')[0].strip()

    start = result_text.find('{')
    end = result_text.rfind('}') + 1
    if start >= 0 and end > start:
        result_text = result_text[start:end]

    return json.loads(result_text)


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


@app.route('/api/entries', methods=['GET'])
def get_entries():
    rows = get_db().execute(
        'SELECT * FROM construction_entries ORDER BY created_at DESC'
    ).fetchall()
    return jsonify([dict(r) for r in rows])


@app.route('/api/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'データがありません'}), 400
    if not data.get('project_name', '').strip():
        return jsonify({'error': 'プロジェクト名は必須です'}), 400
    if not data.get('total_amount'):
        return jsonify({'error': '税込合計金額は必須です'}), 400

    def to_int(v):
        try:
            return int(v) if v not in (None, '') else None
        except (ValueError, TypeError):
            return None

    posting_date = data.get('posting_date') or datetime.now().strftime('%Y-%m-%d')

    db = get_db()
    cur = db.execute(
        '''INSERT INTO construction_entries
               (project_name, project_code, vendor_name, invoice_number,
                invoice_date, amount, tax_amount, total_amount,
                cost_center, wbs_element, gl_account, posting_date,
                description, notes, status, created_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (
            data.get('project_name', '').strip(),
            data.get('project_code') or None,
            data.get('vendor_name') or None,
            data.get('invoice_number') or None,
            data.get('invoice_date') or None,
            to_int(data.get('amount')),
            to_int(data.get('tax_amount')),
            to_int(data.get('total_amount')),
            data.get('cost_center') or None,
            data.get('wbs_element') or None,
            data.get('gl_account') or '1521000',
            posting_date,
            data.get('description') or None,
            data.get('notes') or None,
            '未転送',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        ),
    )
    db.commit()
    return jsonify({'success': True, 'id': cur.lastrowid})


@app.route('/api/entries/<int:entry_id>', methods=['DELETE'])
def delete_entry(entry_id):
    db = get_db()
    db.execute('DELETE FROM construction_entries WHERE id = ?', (entry_id,))
    db.commit()
    return jsonify({'success': True})


@app.route('/api/entries/<int:entry_id>/status', methods=['PATCH'])
def update_status(entry_id):
    data = request.get_json()
    status = data.get('status')
    if status not in ('未転送', '転送済'):
        return jsonify({'error': '無効なステータスです'}), 400
    db = get_db()
    db.execute('UPDATE construction_entries SET status = ? WHERE id = ?', (status, entry_id))
    db.commit()
    return jsonify({'success': True})


@app.route('/api/export/csv', methods=['GET'])
def export_csv():
    """SAP連携用CSV出力（選択IDまたは全件）"""
    ids_param = request.args.get('ids', '')
    db = get_db()

    if ids_param:
        ids = [int(i) for i in ids_param.split(',') if i.strip().isdigit()]
        placeholders = ','.join('?' * len(ids))
        rows = db.execute(
            f'SELECT * FROM construction_entries WHERE id IN ({placeholders}) ORDER BY posting_date, id',
            ids
        ).fetchall()
    else:
        rows = db.execute(
            'SELECT * FROM construction_entries ORDER BY posting_date, id'
        ).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    # SAPインポート用ヘッダー
    writer.writerow([
        '伝票日付', '転記日付', 'GL勘定科目', 'コストセンター', 'WBS要素',
        '金額（税抜）', '消費税額', '金額（税込）', '取引先名', '請求書番号',
        '請求日', 'プロジェクト名', 'プロジェクトコード', '摘要', '備考', 'ステータス'
    ])

    for r in rows:
        writer.writerow([
            r['posting_date'] or '',
            r['posting_date'] or '',
            r['gl_account'] or '1521000',
            r['cost_center'] or '',
            r['wbs_element'] or '',
            r['amount'] if r['amount'] is not None else '',
            r['tax_amount'] if r['tax_amount'] is not None else '',
            r['total_amount'] if r['total_amount'] is not None else '',
            r['vendor_name'] or '',
            r['invoice_number'] or '',
            r['invoice_date'] or '',
            r['project_name'] or '',
            r['project_code'] or '',
            r['description'] or '',
            r['notes'] or '',
            r['status'] or '未転送',
        ])

    # 転送済みに更新
    if rows:
        entry_ids = [r['id'] for r in rows]
        placeholders = ','.join('?' * len(entry_ids))
        db.execute(
            f'UPDATE construction_entries SET status = ? WHERE id IN ({placeholders})',
            ['転送済'] + entry_ids
        )
        db.commit()

    csv_bytes = ('﻿' + output.getvalue()).encode('utf-8')
    filename = f'construction_in_progress_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

    return Response(
        csv_bytes,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5002)
