# API仕様書

## ベースURL
`/api/v1`

## 認証
全エンドポイントにBearerトークン（Azure AD JWT）が必要。

---

## エンドポイント一覧

### KPI系

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/kpi/summary` | 経営サマリー（全KPI最新値） |
| GET | `/kpi/trend` | KPI時系列データ |
| GET | `/kpi/plan-vs-actual` | 計画値 vs 実績値 |

#### GET /kpi/summary
```json
// クエリパラメータ
// fiscal_year: string (例: "FY24") ※省略時は最新期
// quarter: string (例: "Q2", "FY") ※省略時は最新

// レスポンス例
{
  "fiscal_year": "FY24",
  "quarter": "Q4",
  "kpis": {
    "roe": { "value": 8.2, "unit": "%", "plan": 9.0, "yoy": 1.1 },
    "roic": { "value": 7.8, "unit": "%", "plan": 8.0, "yoy": 0.5 },
    "ebitda": { "value": 620000, "unit": "百万円", "plan": 600000, "yoy": 50000 },
    "fcf": { "value": 320000, "unit": "百万円", "plan": 300000, "yoy": 20000 },
    "de_ratio": { "value": 0.51, "unit": "倍", "plan": 0.50, "yoy": -0.03 }
  }
}
```

#### GET /kpi/trend
```json
// クエリパラメータ
// kpi: string (例: "roe", "ebitda")
// from_fy: string (例: "FY20")
// to_fy: string (例: "FY24")
// granularity: "quarter" | "annual"

// レスポンス例
{
  "kpi": "ebitda",
  "unit": "百万円",
  "data": [
    { "period": "FY20", "actual": 480000, "plan": null },
    { "period": "FY21", "actual": 550000, "plan": null },
    { "period": "FY22", "actual": 590000, "plan": null },
    { "period": "FY23", "actual": 610000, "plan": 600000 },
    { "period": "FY24", "actual": 620000, "plan": 600000 }
  ]
}
```

### セグメント系

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/segments` | セグメント一覧 |
| GET | `/segments/{segment_code}/profit` | セグメント別損益時系列 |
| GET | `/segments/breakdown` | 全セグメント構成比 |

### 中計KPI達成度

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/midterm-plan/achievement` | 中計KPI達成度（全指標） |
| GET | `/midterm-plan/targets` | 中計ターゲット一覧 |

### ESG・非財務

| メソッド | パス | 説明 |
|---------|------|------|
| GET | `/esg/co2` | CO2排出量推移 |
| GET | `/esg/summary` | ESG KPI一覧 |

---

## エラーレスポンス
```json
{
  "error": {
    "code": "DATA_NOT_FOUND",
    "message": "指定された期間のデータが見つかりません",
    "detail": "fiscal_year=FY19 のデータは未登録です"
  }
}
```

_最終更新: 2026-05-27 / 担当: ソフト開発部_
