#!/usr/bin/env python3
"""計算結果_729.xlsx を コンパクトな data.json に変換する。
Excelは読み取りのみ。出力はこのフォルダの data.json。"""
import openpyxl, json, os
from datetime import datetime, timedelta

SRC = "/Users/jummatsuchida/Desktop/エンジニアのミカタ/ファイナンス資料/LP作成/計算結果_729.xlsx"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")

# レバー列の順序（xlsxの列順）
PARAM_KEYS = ["PP入社数", "PP離職率", "粗利率", "営業成約件数", "採用単価", "管理部門人数"]
LEVELS = ["楽観", "標準", "悲観"]
LEVEL_IDX = {"楽観": 0, "標準": 1, "悲観": 2}

# KPI 57項目の単位（行順固定）。money=百万円(÷1e6), pct=率, yen=円, ppl=人, ken=件, section=見出し
UNITS = [
    "money","ppl","ppl","ppl","ppl","yen","money","pct","money","money",   # 0-9
    "money","money","money","pct","pct","money","money","money","ppl","ken", # 10-19
    "ken","yen","money","yen","money","ppl","ken","yen","ppl","money",       # 20-29
    "money","yen","yen","yen","money","ppl","yen","money","section","ppl",   # 30-39
    "ppl","yen","pct","ken","ppl","pct","ppl","ppl","ppl","ppl",             # 40-49
    "yen","pct","section","money","money","money","money",                   # 50-56
]
UNIT_LABEL = {"money":"百万円","pct":"%","yen":"円","ppl":"人","ken":"件","section":""}

def excel_serial_to_ym(serial):
    d = datetime(1899, 12, 30) + timedelta(days=int(serial))
    return f"{d.year}-{d.month:02d}"

def scale(unit, v):
    if v is None:
        return None
    if not isinstance(v, (int, float)):
        return None
    if unit == "money":
        return round(v / 1_000_000, 2)
    if unit == "pct":
        return round(v, 5)
    if unit == "yen":
        return round(v, 0)
    return round(v, 2)

print("読み込み中...", SRC)
wb = openpyxl.load_workbook(SRC, data_only=True, read_only=True)
ws = wb["計算結果"]
it = ws.iter_rows(values_only=True)
hdr = list(next(it))

# 期間列: col8-13 年度(6), col14-37 四半期(24), col38-109 月次(72)
year_labels = [str(hdr[i]) for i in range(8, 14)]
quarter_labels = [str(hdr[i]) for i in range(14, 38)]
month_labels = [excel_serial_to_ym(hdr[i]) for i in range(38, 110)]

rows = list(it)
assert len(rows) == 41553, f"想定外の行数: {len(rows)}"
NK = 57  # KPI行数

# KPI定義（最初のコンボから）
kpis = []
for j in range(NK):
    name = rows[j][7]
    u = UNITS[j]
    kpis.append({"name": (name or "").strip(), "unit": UNIT_LABEL[u], "u": u,
                 "section": u == "section"})

data = {}
for i in range(0, len(rows), NK):
    block = rows[i:i+NK]
    p = block[0][1:7]
    key = "".join(str(LEVEL_IDX[p[k]]) for k in range(6))
    arr = []
    for j in range(NK):
        u = UNITS[j]
        row_j = block[j]
        # section行など末尾セルが切り詰められた行に対応（不足分はNone）
        vals = [scale(u, row_j[c] if c < len(row_j) else None) for c in range(8, 110)]
        arr.append(vals)
    data[key] = arr

out = {
    "params": [{"key": k, "levels": LEVELS} for k in PARAM_KEYS],
    "periods": {"year": year_labels, "quarter": quarter_labels, "month": month_labels},
    "kpis": kpis,
    "data": data,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))
sz = os.path.getsize(OUT)
print(f"出力: {OUT}  ({sz/1_000_000:.1f} MB)  combos={len(data)} kpis={NK}")
print("年度:", year_labels)
print("月次先頭/末尾:", month_labels[0], "...", month_labels[-1])
