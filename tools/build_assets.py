#!/usr/bin/env python3
"""Global asset market-cap ranking poster (TOP 20). Usage: python3 tools/build_assets.py assets.json out.png
assets.json: {"date": "2026.11.20 (금)", "asof": "01:35 KST 기준", "source": "ARASEO (araseo.xyz) · companiesmarketcap.com",
 "rows": [[순위, "변동"(""|"▲1"|"▼1"|"NEW"), "이름", "분류", "티커·국가"(없으면 ""), "가격", "시가총액", 오늘등락률(숫자 %)], ... 20개]}"""
import json, sys, subprocess, html, os, tempfile
E = html.escape
CAT = {"귀금속": "#ffc531", "암호화폐": "#f7931a", "지수 ETF": "#8c9eff"}

def main():
    d = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    rows = ""
    for r, mv, name, cat, tk, price, cap, chg in d["rows"][:20]:
        col = CAT.get(cat, "#3fc1c9"); hot = ' class="hot"' if cat == "암호화폐" else ""
        mvh = ""
        if mv:
            c = "#2fd08a" if mv.startswith("▲") else ("#ff5d6c" if mv.startswith("▼") else "#ffc531")
            mvh = f'<i style="color:{c}">{E(mv)}</i>'
        cc = "grn" if chg > 0 else ("red" if chg < 0 else "")
        rows += (f'<tr{hot}><td class="rk"><b>{r}</b>{mvh}</td><td class="nm"><span class="dot" style="background:{col}"></span><div><b>{E(name)}</b>'
                 f'<small>{E(cat)}{" · " + E(tk) if tk else ""}</small></div></td><td>{E(price)}</td><td class="cap">{E(cap)}</td><td class="{cc}">{chg:+.2f}%</td></tr>')
    H = 330 + 71*min(20, len(d["rows"])) + 110
    page = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:{H}px;background:#0b0f1a;color:#e9edf5;font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;padding:56px 56px 40px;position:relative;overflow:hidden}}
body:before{{content:"";position:absolute;right:-220px;top:-220px;width:640px;height:640px;border-radius:50%;background:radial-gradient(circle,#f7931a33,transparent 65%)}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #f7931a;padding-bottom:22px;position:relative}}
.k{{font-size:22px;letter-spacing:6px;color:#f7931a;font-weight:700}}.k span{{letter-spacing:2px;color:#9aa6bd;font-weight:500}}
h1{{font-size:62px;font-weight:900;line-height:1.1;margin-top:6px}}
.date{{text-align:right;font-size:24px;color:#9aa6bd;line-height:1.5}}.date b{{color:#fff;font-size:30px}}
.sub{{font-size:23px;color:#aab4c8;margin:20px 0 18px}}
table{{width:100%;border-collapse:collapse;background:#111727;border-radius:16px;overflow:hidden}}
th{{font-size:19px;color:#8b97b0;font-weight:500;padding:12px 14px;background:#161d31;text-align:right}}
th:nth-child(1),th:nth-child(2){{text-align:left}}
td{{height:71px;padding:0 14px;text-align:right;font-size:25px;font-weight:700;border-top:1px solid #1e2740;white-space:nowrap}}
td.rk{{text-align:left;width:112px;padding-left:22px}}td.rk b{{font-size:29px;font-weight:900;color:#f7931a;display:inline-block;width:40px}}
td.rk i{{font-style:normal;font-size:17px;font-weight:700}}
td.nm{{text-align:left;display:flex;align-items:center;gap:12px;height:71px}}
td.nm b{{font-size:25px;display:block;line-height:1.2}}td.nm small{{font-size:16px;color:#8b97b0;font-weight:400}}
.dot{{width:10px;height:38px;border-radius:5px;flex:none}}
td.cap{{color:#fff;font-size:27px;font-weight:900}}
tr.hot td{{background:#2a1c08}}tr.hot td.nm b{{color:#f7931a}}
.red{{color:#ff5d6c}}.grn{{color:#2fd08a}}
.lg{{display:flex;gap:22px;margin-top:16px;font-size:18px;color:#aab4c8}}.lg span{{display:flex;align-items:center;gap:7px}}.lg i{{width:10px;height:18px;border-radius:5px;display:inline-block}}
.ft{{position:absolute;left:56px;right:56px;bottom:24px;font-size:17px;color:#6c7890;line-height:1.5}}
</style></head><body>
<div class="top"><div><div class="k">GLOBAL ASSETS <span>· by Moni</span></div><h1>전체 자산 시총 순위</h1></div>
<div class="date"><b>{E(d["date"])}</b><br>{E(d["asof"])}</div></div>
<p class="sub">금부터 비트코인까지, 세상에서 가장 큰 자산 TOP 20</p>
<table><tr><th>순위</th><th>자산</th><th>가격</th><th>시가총액</th><th>오늘</th></tr>{rows}</table>
<div class="lg"><span><i style="background:#3fc1c9"></i>주식</span><span><i style="background:#ffc531"></i>귀금속</span><span><i style="background:#f7931a"></i>암호화폐</span><span><i style="background:#8c9eff"></i>ETF</span><span>▲▼ 전일 대비 순위 변동</span></div>
<div class="ft">자료: {E(d.get("source",""))} · 귀금속 시가총액은 추정치 · 투자 권유가 아닌 정보 제공용입니다.</div>
</body></html>"""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); tmp.write(page); tmp.close()
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size=1080,{H}", f"--screenshot={os.path.abspath(out)}", "file://"+tmp.name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
