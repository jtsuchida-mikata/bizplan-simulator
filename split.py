#!/usr/bin/env python3
"""data.json を Web が読む形式へ分割する。
  - meta.json … params / periods / kpis（軽量・data抜き）
  - combos/{6桁キー}.json … 各シナリオの [57 KPI][102 期間] 配列
data.json は convert.py が生成（.gitignore 済み）。本スクリプトの出力はコミット対象。"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "data.json")
COMBO_DIR = os.path.join(HERE, "combos")

with open(SRC, encoding="utf-8") as f:
    d = json.load(f)

meta = {"params": d["params"], "periods": d["periods"], "kpis": d["kpis"]}
with open(os.path.join(HERE, "meta.json"), "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))

os.makedirs(COMBO_DIR, exist_ok=True)
n = 0
for key, arr in d["data"].items():
    with open(os.path.join(COMBO_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
        json.dump(arr, f, ensure_ascii=False, separators=(",", ":"))
    n += 1

print(f"meta.json 出力 (kpis={len(meta['kpis'])}, params={len(meta['params'])})")
print(f"combos/ 出力: {n} ファイル")
