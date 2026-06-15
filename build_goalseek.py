#!/usr/bin/env python3
"""
goalseek.json を生成する。
combos/*.json（729シナリオ・全KPIの102期間配列）から、
逆引きダッシュボード「いいとこ選択肢ボード」が使う最小限の値だけを抜き出す。

抜き出すKPI（年度6期分のみ＝index 0..5）:
  12 = 営業利益（百万円）
  44 = PP入社数（累計/期, 人）
  45 = PP離職率（%）
   7 = 粗利率（%）
   0 = 売上高（百万円）       … トレードオフ盤の制約式 営業利益=売上×粗利率−販管費 に使用
   8 = 販管費総額（百万円）   … 同上

出力: { "yearLabels":[...6...], "data": { "<6桁キー>": [op6, nyu6, ri6, ar6, rev6, sga6], ... } }
  各値は6要素の配列（年度）。op/nyu/rev/sgaは丸め、率は小数4桁。

data.json の構造変更なし・値更新時は split.py の後にこれを実行すれば最新化される。
"""
import json, glob, os

SRC_DIR = os.path.join(os.path.dirname(__file__), "combos")
META = os.path.join(os.path.dirname(__file__), "meta.json")
OUT = os.path.join(os.path.dirname(__file__), "goalseek.json")

KPI = {"op": 12, "nyu": 44, "ri": 45, "ar": 7, "rev": 0, "sga": 8}
YEARS = 6  # 年度は先頭6期


def main():
    meta = json.load(open(META, encoding="utf-8"))
    year_labels = [str(l).replace(" 計", "").strip() for l in meta["periods"]["year"]]

    data = {}
    for f in sorted(glob.glob(os.path.join(SRC_DIR, "*.json"))):
        key = os.path.basename(f)[:6]
        d = json.load(open(f, encoding="utf-8"))
        op = [round(d[KPI["op"]][y]) for y in range(YEARS)]
        nyu = [round(d[KPI["nyu"]][y]) for y in range(YEARS)]
        ri = [round(d[KPI["ri"]][y], 4) for y in range(YEARS)]
        ar = [round(d[KPI["ar"]][y], 4) for y in range(YEARS)]
        rev = [round(d[KPI["rev"]][y]) for y in range(YEARS)]
        sga = [round(d[KPI["sga"]][y]) for y in range(YEARS)]
        data[key] = [op, nyu, ri, ar, rev, sga]

    out = {"yearLabels": year_labels, "data": data}
    with open(OUT, "w", encoding="utf-8") as fp:
        json.dump(out, fp, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {OUT}: {len(data)} scenarios, {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
