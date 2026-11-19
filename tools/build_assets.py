#!/usr/bin/env python3
"""Global asset market-cap ranking poster (TOP 20). Usage: python3 tools/build_assets.py assets.json out.png
assets.json: {"date": "2026.11.20 (금)", "asof": "01:35 KST 기준", "source": "ARASEO (araseo.xyz) · companiesmarketcap.com",
 "rows": [[순위, "변동"(""|"▲1"|"▼1"|"NEW"), "이름", "분류", "티커"(없으면 ""), "가격", "시가총액", 오늘등락률(숫자 %), "국가"(없으면 ""), 1년등락률(숫자 % 또는 null)], ... 20개]}
회사 로고는 상표라 그리지 않고, 업종을 나타내는 일반 아이콘 배지를 쓴다(종목 코드는 이름 아래 줄에 표시). 국기는 이모지로 표시한다."""
import json, sys, subprocess, html, os, tempfile
E = html.escape
CAT = {"귀금속": "#ffc531", "암호화폐": "#f7931a", "지수 ETF": "#8c9eff"}
FLAG = {"미국": "🇺🇸", "대만": "🇹🇼", "사우디": "🇸🇦", "한국": "🇰🇷", "중국": "🇨🇳", "일본": "🇯🇵", "영국": "🇬🇧", "네덜란드": "🇳🇱", "스위스": "🇨🇭", "프랑스": "🇫🇷", "독일": "🇩🇪", "": "🌐"}
PAL = ["#3b82f6", "#10b981", "#8b5cf6", "#ef4444", "#0ea5e9", "#f59e0b", "#ec4899", "#14b8a6", "#6366f1", "#84cc16"]
SPECIAL = {"금": ("Au", "#d4a017"), "은": ("Ag", "#9aa3ad"), "백금": ("Pt", "#b8c4cc"), "비트코인": ("₿", "#f7931a"), "이더리움": ("Ξ", "#5b6ee1")}
W = 'fill="#fff"'; L = 'fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"'
SECTOR_ICON = [   # (분류에 들어 있는 낱말, 업종 아이콘) - 회사 로고가 아닌 일반 아이콘
 ("반도체", f'<rect x="7.5" y="7.5" width="9" height="9" rx="1.5" {W}/><path d="M10 4v3M14 4v3M10 17v3M14 17v3M4 10h3M4 14h3M17 10h3M17 14h3" {L}/>'),
 ("소프트웨어", f'<path d="M9 8l-4 4 4 4M15 8l4 4-4 4M13 6l-2 12" {L}/>'),
 ("인터넷", f'<circle cx="12" cy="12" r="8" {L}/><ellipse cx="12" cy="12" rx="3.4" ry="8" {L}/><path d="M4 12h16" {L}/>'),
 ("하드웨어", f'<rect x="7.5" y="3.5" width="9" height="17" rx="2" {L}/><circle cx="12" cy="17.3" r="1" {W}/>'),
 ("우주", f'<path d="M12 2.5c3 2.6 4.2 6.5 4.2 10.5H7.8c0-4 1.2-7.9 4.2-10.5z" {W}/><path d="M7.8 12.5 4.800 17h3zM16.2 12.5l3 4.5h-3zM10.3 15h3.400L12 21z" {W}/>'),
 ("에너지", f'<path d="M12 3c4 5 6 8 6 11a6 6 0 0 1-12 0c0-3 2-6 6-11z" {W}/>'),
 ("자동차", f'<path d="M3 14.5l2-5.5h14l2 5.5V18H3z" {W}/><circle cx="7.5" cy="18" r="2" fill="#fff" stroke="#0b0f1a" stroke-width="1.2"/><circle cx="16.5" cy="18" r="2" fill="#fff" stroke="#0b0f1a" stroke-width="1.2"/>'),
 ("금융", f'<path d="M3 9.5 12 4l9 5.5V11H3z" {W}/><path d="M6 12.5v5M10 12.5v5M14 12.5v5M18 12.5v5M3.5 20h17" {L}/>'),
 ("결제", f'<rect x="3.5" y="6" width="17" height="12" rx="2" {L}/><path d="M3.5 10.5h17" {L}/>'),
 ("헬스", f'<path d="M9.5 4h5v5.5H20v5h-5.5V20h-5v-5.5H4v-5h5.5z" {W}/>'),
 ("ETF", f'<path d="M5 20V13M10 20V8M15 20v-9M20 20V4" fill="none" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'),
 ("소비재", f'<path d="M5.5 8.5h13L17.3 20H6.700z" {W}/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5" {L}/>'),
 ("통신", f'<path d="M12 20v-7M8 9a5.5 5.5 0 0 1 8 0M5 6a10 10 0 0 1 14 0" {L}/>'),
]
def badge(name, tk, cat=""):
    if name in ("금", "은", "백금"):
        c = {"금": ("#f6c945", "#a87400"), "은": ("#dfe5ea", "#7b858f"), "백금": ("#eef3f6", "#8d9aa3")}[name]
        return (f'<span class="bd" style="background:#1c2236"><svg viewBox="0 0 24 24" width="36" height="36"><path d="M7.5 9h9l3.5 8H4z" fill="{c[0]}" stroke="{c[1]}" stroke-width="1"/>'
                f'<path d="M7.5 9h9l-1.2 3H8.700z" fill="#fff" opacity=".45"/></svg></span>')
    if name in SPECIAL:
        t, c = SPECIAL[name]
        return f'<span class="bd" style="background:{c};font-size:28px;border-radius:50%">{E(t)}</span>'
    key = (tk.split(".")[0] if tk else name)
    c = PAL[sum(map(ord, key)) % len(PAL)]
    ico = next((svg for kw, svg in SECTOR_ICON if kw in cat), f'<circle cx="12" cy="12" r="6" {W}/>')
    return f'<span class="bd" style="background:{c}"><svg viewBox="0 0 24 24" width="32" height="32">{ico}</svg></span>'

def main():
    d = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    rows = ""
    for row in d["rows"][:20]:
        r, mv, name, cat, tk, price, cap, chg = row[:8]
        country = row[8] if len(row) > 8 else ""; y1 = row[9] if len(row) > 9 else None
        if y1 is None: y1h = '<td class="dim">–</td>'
        elif isinstance(y1, str): y1h = f'<td class="dim" style="font-size:18px">{E(y1)}</td>'
        else: y1h = f'<td class="{"grn" if y1 > 0 else "red"}">{y1:+.1f}%</td>'
        flag = FLAG.get(country, "🌐")
        col = CAT.get(cat, "#3fc1c9"); hot = ' class="hot"' if cat == "암호화폐" else ""
        mvh = ""
        if mv:
            c = "#2fd08a" if mv.startswith("▲") else ("#ff5d6c" if mv.startswith("▼") else "#ffc531")
            mvh = f'<i style="color:{c}">{E(mv)}</i>'
        cc = "grn" if chg > 0 else ("red" if chg < 0 else "")
        rows += (f'<tr{hot}><td class="rk"><b>{r}</b>{mvh}</td><td class="nm"><span class="dot" style="background:{col}"></span>{badge(name, tk, cat)}<div><b>{E(name)} <em>{flag}</em></b>'
                 f'<small>{E(cat)}{" · " + E(tk) if tk else ""}{" · " + E(country) if country else ""}</small></div></td><td>{E(price)}</td><td class="cap">{E(cap)}</td><td class="{cc}">{chg:+.2f}%</td>{y1h}</tr>')
    H = 330 + 71*min(20, len(d["rows"])) + 135
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
td{{height:71px;padding:0 11px;text-align:right;font-size:23px;font-weight:700;border-top:1px solid #1e2740;white-space:nowrap}}
td.rk{{text-align:left;width:104px;padding-left:18px}}
.bd{{flex:none;width:46px;height:46px;border-radius:12px;color:#fff;font-weight:900;display:flex;align-items:center;justify-content:center;font-family:"DejaVu Sans","Noto Sans CJK KR",sans-serif;letter-spacing:-.5px}}
td.nm em{{font-style:normal;font-family:"Noto Color Emoji";font-size:21px;margin-left:4px}}
.dim{{color:#56617a}}td.rk b{{font-size:29px;font-weight:900;color:#f7931a;display:inline-block;width:40px}}
td.rk i{{font-style:normal;font-size:17px;font-weight:700}}
td.nm{{text-align:left;display:flex;align-items:center;gap:10px;height:71px}}
td.nm b{{font-size:23px;display:block;line-height:1.25}}td.nm small{{font-size:16px;color:#8b97b0;font-weight:400}}
.dot{{width:7px;height:38px;border-radius:5px;flex:none}}
td.cap{{color:#fff;font-size:24px;font-weight:900}}
tr.hot td{{background:#2a1c08}}tr.hot td.nm b{{color:#f7931a}}
.red{{color:#ff5d6c}}.grn{{color:#2fd08a}}
.lg{{display:flex;gap:22px;margin-top:16px;font-size:18px;color:#aab4c8}}.lg span{{display:flex;align-items:center;gap:7px}}.lg i{{width:10px;height:18px;border-radius:5px;display:inline-block}}
.ft{{position:absolute;left:56px;right:56px;bottom:24px;font-size:17px;color:#6c7890;line-height:1.5}}
</style></head><body>
<div class="top"><div><div class="k">GLOBAL ASSETS <span>· by Moni</span></div><h1>전체 자산 시총 순위</h1></div>
<div class="date"><b>{E(d["date"])}</b><br>{E(d["asof"])}</div></div>
<p class="sub">금부터 비트코인까지, 세상에서 가장 큰 자산 TOP 20</p>
<table><tr><th>순위</th><th>자산</th><th>가격</th><th>시가총액</th><th>오늘</th><th>1년</th></tr>{rows}</table>
<div class="lg"><span><i style="background:#3fc1c9"></i>주식</span><span><i style="background:#ffc531"></i>귀금속</span><span><i style="background:#f7931a"></i>암호화폐</span><span><i style="background:#8c9eff"></i>ETF</span><span>▲▼ 전일 대비 순위 변동</span></div>
<div class="ft">자료: {E(d.get("source",""))} · {E(d.get("y1_note","1년 등락률은 주가 기준"))} · 귀금속 시가총액은 추정치 · 투자 권유가 아닌 정보 제공용입니다.</div>
</body></html>"""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); tmp.write(page); tmp.close()
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size=1080,{H}", f"--screenshot={os.path.abspath(out)}", "file://"+tmp.name], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
