#!/usr/bin/env python3
"""Crypto briefing poster builder.
Usage: python3 tools/build.py data.json out.png
data.json:
{
 "title": "크립토 아침 브리핑", "date": "2026.11.20 (금)", "asof": "08:55 KST 기준",
 "fx": 1330.0, "fx_label": "원/달러 환율 (주간 종가)",
 "fear_greed": 10,     (optional, 0~100 숫자. 라벨·색·토끼 표정 아이콘은 스크립트가 자동으로 고른다:
                        0-24 극단적 공포 / 25-44 공포 / 45-55 중립 / 56-75 탐욕 / 76-100 극단적 탐욕)
 "dominance": {"total_mcap": 2182549664066, "asof": "CoinLore",        (optional section)
               "top10": [["BTC",1272553557787],["ETH",221015637828],["USDT",...], ... 시총 상위 10개]},
 "coins": {"BTC": {"usd": 63830.1, "chg24h": -0.55 (또는 "usd_open24h": 64148), "krw": 86611000,
                   "d": "2026-11-19:86586000,2026-11-18:...",   (업비트 일봉 종가, date:price)
                   "w": "...", "m": "..."}, "ETH": {...}, "SOL": {...}, "XRP": {...}},
 "onchain": {"realized": 53477, "realized_note": "11/18 기준", "delta": 30800, "delta_note": "11/18 기준"},
            (optional. BTC 실현가격·델타가격(달러). 값이 있으면 포스터 높이가 2030px로 늘어난다.
             이때 build_issue.py의 issue.json에도 "height": 2030 을 넣어 좌우 높이를 맞춘다. delta를 못 구하면 delta 키를 뺀다.)
 "issues": [["제목", "한 줄 설명"], ... 5개]
}
강조 표기(반드시 사용): issues의 설명(둘째 항목)에만 쓴다. 제목은 강조 없이 흰색 그대로 둔다.
  [[...]] = 숫자·금액·비율·날짜 (주황색)   예: "[[18일]] 하루 [[3억 달러]] 이상 순유출"
  **...** = 기업·코인·기관·상품 등 명칭 (하늘색)  예: "**BTC** 한때 [[$62K]]대"
한 줄에 1~3곳만 강조한다. 우측 하단에는 "1/2 Page"가 자동으로 들어간다.
Prints computed numbers as JSON (use them for the Telegram caption) and writes the PNG.
RSI = Wilder RSI(14); the newest candle is replaced by the live KRW price.
"""
import json, sys, subprocess, html, os, tempfile

import re
def R(t):
    """escape + highlight markup"""
    t = html.escape(t)
    t = re.sub(r"\[\[(.+?)\]\]", r'<span class="num">\1</span>', t)
    return re.sub(r"\*\*(.+?)\*\*", r'<span class="nm">\1</span>', t)

def parse(s):
    d = {}
    for t in s.replace("\n", "").split(","):
        t = t.strip()
        if t:
            k, v = t.rsplit(":", 1); d[k.strip()] = float(v)
    return d

def rsi(c, n=14):
    g = [max(c[i]-c[i-1], 0) for i in range(1, len(c))]
    l = [max(c[i-1]-c[i], 0) for i in range(1, len(c))]
    ag, al = sum(g[:n])/n, sum(l[:n])/n
    for i in range(n, len(g)):
        ag = (ag*(n-1)+g[i])/n; al = (al*(n-1)+l[i])/n
    return 100.0 if al == 0 else 100-100/(1+ag/al)

ICON = {"BTC": "₿", "ETH": "Ξ", "SOL": "S", "XRP": "X"}

def dominance(dm):
    """BTC.D / ETH.D / OTHERS.D(시총 상위 10개 제외) / 스테이블(USDT+USDC) 비중(%)"""
    tot = float(dm["total_mcap"]); caps = {k.upper(): float(v) for k, v in dm["top10"][:10]}
    if len(caps) < 10: sys.exit("dominance: top10 needs 10 coins")
    pct = lambda v: round(v/tot*100, 2)
    return {"btc_d": pct(caps["BTC"]), "eth_d": pct(caps["ETH"]),
            "others_d": pct(tot-sum(caps.values())),
            "stable_d": pct(caps.get("USDT", 0)+caps.get("USDC", 0)), "total_mcap": tot}

# ---------- pill icons (original SVG drawings) ----------
def _bunny(inner):
    return ('<svg class="pi" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
            '<g stroke="#5a3b3b" stroke-width="1.6">'
            '<ellipse cx="33" cy="24" rx="10" ry="23" fill="#fff" transform="rotate(-14 33 24)"/>'
            '<ellipse cx="67" cy="24" rx="10" ry="23" fill="#fff" transform="rotate(14 67 24)"/></g>'
            '<ellipse cx="33" cy="26" rx="5" ry="16" fill="#f7a8b0" transform="rotate(-14 33 26)"/>'
            '<ellipse cx="67" cy="26" rx="5" ry="16" fill="#f7a8b0" transform="rotate(14 67 26)"/>'
            '<ellipse cx="50" cy="64" rx="37" ry="31" fill="#fff" stroke="#5a3b3b" stroke-width="1.6"/>'
            + inner + '</svg>')
_BLUSH = '<ellipse cx="25" cy="72" rx="7.5" ry="4.5" fill="#ffb3bd"/><ellipse cx="75" cy="72" rx="7.5" ry="4.5" fill="#ffb3bd"/>'
_EYES = '<rect x="33" y="52" width="9" height="17" rx="4.5" fill="#111"/><rect x="58" y="52" width="9" height="17" rx="4.5" fill="#111"/>'
BUNNY = {
 # 극단적 공포: 쪼그라든 눈동자, 벌어진 입, 눈물, 이마의 파란 그늘
 "extreme_fear": _bunny('<path d="M26 40 Q50 30 74 40 L74 46 Q50 38 26 46Z" fill="#9db8ff" opacity=".75"/>'
   '<g stroke="#6f8fe8" stroke-width="2" stroke-linecap="round"><path d="M40 37v7M50 35v8M60 37v7"/></g>'
   '<g stroke="#111" stroke-width="2.6" stroke-linecap="round" fill="none"><path d="M30 52l11 4M70 52l-11 4"/></g>'
   '<circle cx="37" cy="62" r="3.6" fill="#111"/><circle cx="63" cy="62" r="3.6" fill="#111"/>'
   '<path d="M33 70q-3 8 0 13q4-5 0-13z" fill="#6fb6ff"/><path d="M67 70q3 8 0 13q-4-5 0-13z" fill="#6fb6ff"/>'
   '<path d="M41 80q3-5 6 0t6 0t6 0q-3 9-9 9t-9-9z" fill="#5a2a33"/>'),
 # 공포: 걱정 눈썹, 처진 입, 식은땀
 "fear": _bunny(_BLUSH + '<g stroke="#111" stroke-width="2.6" stroke-linecap="round" fill="none"><path d="M30 50l11-4M70 50l-11-4"/></g>'
   '<rect x="34" y="54" width="8" height="14" rx="4" fill="#111"/><rect x="58" y="54" width="8" height="14" rx="4" fill="#111"/>'
   '<path d="M43 84q7-7 14 0" stroke="#111" stroke-width="2.6" stroke-linecap="round" fill="none"/>'
   '<path d="M80 44q-5 9 0 13q5-4 0-13z" fill="#6fb6ff"/>'),
 # 중립: 원본과 같은 타원 눈, 일자 입
 "neutral": _bunny(_BLUSH + _EYES + '<path d="M44 82h12" stroke="#111" stroke-width="2.6" stroke-linecap="round"/>'),
 # 탐욕: 웃는 눈, 미소
 "greed": _bunny(_BLUSH + '<g stroke="#111" stroke-width="3.2" stroke-linecap="round" fill="none">'
   '<path d="M31 63q6.5-10 13 0M56 63q6.5-10 13 0"/><path d="M41 78q9 9 18 0"/></g>'),
 # 극단적 탐욕: 별 눈, 활짝 벌린 입, 반짝이
 "extreme_greed": _bunny(_BLUSH
   + '<path id="st" d="M0-9 2.6-2.8 9-2.8 3.9 1.6 5.6 8 0 4.2-5.6 8-3.9 1.6-9-2.8-2.6-2.8z" fill="#ffb020" stroke="#c97a00" stroke-width=".8" transform="translate(37 60)"/>'
   '<path d="M0-9 2.6-2.8 9-2.8 3.9 1.6 5.6 8 0 4.2-5.6 8-3.9 1.6-9-2.8-2.6-2.8z" fill="#ffb020" stroke="#c97a00" stroke-width=".8" transform="translate(63 60)"/>'
   '<path d="M38 75h24q-1 14-12 14t-12-14z" fill="#5a2a33"/><path d="M44 85q6-5 12 0q-6 5-12 0z" fill="#ff8fa0"/>'
   '<g fill="#ffd76a"><path d="M88 40l1.8 4.6 4.6 1.8-4.6 1.8L88 52.8l-1.8-4.6-4.6-1.8 4.6-1.8z"/><path d="M11 44l1.3 3.3 3.3 1.3-3.3 1.3L11 53.5l-1.3-3.3-3.3-1.3 3.3-1.3z"/></g>'),
}
FG_LEVELS = [(24, "extreme_fear", "극단적 공포", "#ff5d6c"), (44, "fear", "공포", "#ff9a57"), (55, "neutral", "중립", "#e9edf5"),
             (75, "greed", "탐욕", "#7fdc8f"), (100, "extreme_greed", "극단적 탐욕", "#2fd08a")]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bunny import bunny as _bunny_svg
BUNNY_STYLE = "A"   # "A" = 흰 토끼(첫 번째 캐릭터), "B" = 크림색 토끼(두 번째 캐릭터)
def fear_greed(v):
    """0~100 값을 (라벨, 색, 토끼 아이콘)으로. 0-24 극단적 공포 / 25-44 공포 / 45-55 중립 / 56-75 탐욕 / 76-100 극단적 탐욕"""
    for hi, key, label, color in FG_LEVELS:
        if v <= hi: return label, color, _bunny_svg(BUNNY_STYLE, key)
    return FG_LEVELS[-1][2], FG_LEVELS[-1][3], _bunny_svg(BUNNY_STYLE, "extreme_greed")

DOLLAR_ICON = ('<svg class="pi" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="42" fill="#2e9e5b" stroke="#1d6b3d" stroke-width="4"/>'
               '<circle cx="50" cy="50" r="33" fill="none" stroke="#7fdca0" stroke-width="2.5" stroke-dasharray="3 5"/>'
               '<text x="50" y="69" font-size="56" font-weight="900" text-anchor="middle" fill="#fff" font-family="DejaVu Sans,Arial,sans-serif">$</text></svg>')
KIMCHI_ICON = ('<svg class="pi" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
               '<path d="M22 50q-4-22 12-27q6-10 17-6q10-7 19 2q14 2 11 31z" fill="#e2452f" stroke="#a3271a" stroke-width="2.5"/>'
               '<g fill="none" stroke="#ffb09a" stroke-width="3" stroke-linecap="round"><path d="M34 46q0-13 8-18M50 46q-1-14 4-22M65 46q2-11-2-18"/></g>'
               '<g fill="#6cc04a"><ellipse cx="29" cy="30" rx="6" ry="3.5" transform="rotate(-35 29 30)"/><ellipse cx="74" cy="27" rx="6" ry="3.5" transform="rotate(30 74 27)"/><ellipse cx="52" cy="19" rx="5" ry="3"/></g>'
               '<path d="M10 50h80q-2 26-22 34H32q-20-8-22-34z" fill="#f4f1ea" stroke="#8a8170" stroke-width="2.5"/>'
               '<path d="M18 60q30 8 64 0" fill="none" stroke="#5b8fd6" stroke-width="3"/><rect x="36" y="84" width="28" height="6" rx="2" fill="#d9d4c7" stroke="#8a8170" stroke-width="2"/></svg>')

def usd_fmt(v):
    return f"${v:,.0f}" if v >= 10000 else (f"${v:,.2f}" if v >= 10 else f"${v:,.4f}")

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8")); out_png = sys.argv[2]
    fx = float(data["fx"]); res = {}; rows = ""
    for sym, c in data["coins"].items():
        r = {"usd": c["usd"], "krw": c["krw"],
             "chg": round(float(c["chg24h"]), 2) if "chg24h" in c else round((c["usd"]/c["usd_open24h"]-1)*100, 2),
             "kimp": round((c["krw"]/(c["usd"]*fx)-1)*100, 2)}
        for tf in "dwm":
            m = parse(c[tf]); keys = sorted(m)
            if len(keys) < 30: sys.exit(f"{sym} {tf}: candles too few ({len(keys)})")
            r[tf+"_latest"] = keys[-1]
            s = [m[k] for k in keys]; s[-1] = c["krw"]
            r["rsi_"+tf] = round(rsi(s), 1)
        res[sym] = r
        cls = "grn" if r["chg"] >= 0 else "red"
        def cell(v): return f'<td class="{"os" if v < 30 else ("ob" if v > 70 else "")}">{v:.1f}</td>'
        rows += (f'<tr><td class="c"><span class="ic ic-{sym}">{ICON.get(sym, sym[0])}</span>{sym}</td><td>{usd_fmt(r["usd"])}<small>{r["krw"]:,.0f}원</small></td>'
                 f'<td class="{cls}">{r["chg"]:+.2f}%</td><td class="org">{r["kimp"]:+.2f}%</td>'
                 f'{cell(r["rsi_d"])}{cell(r["rsi_w"])}{cell(r["rsi_m"])}</tr>')
    first = next(iter(res.values()))
    pills = ""
    fg = data.get("fear_greed_value", data.get("fear_greed"))
    if fg not in (None, ""):
        m = re.search(r"\d+", str(fg))
        if m:
            v = int(m.group()); label, color, face = fear_greed(v); res["_fear_greed"] = {"value": v, "label": label}
            pills += f'<div class="pill"><div><span>공포·탐욕 지수</span><b style="color:{color}">{v} · {label}</b></div>{face}</div>'
    pills += f'<div class="pill"><div><span>{html.escape(data.get("fx_label","원/달러 환율"))}</span><b>{fx:,.0f}원</b></div>{DOLLAR_ICON}</div>'
    pills += f'<div class="pill"><div><span>김치프리미엄 (BTC)</span><b class="org">{res["BTC"]["kimp"]:+.2f}%</b></div>{KIMCHI_ICON}</div>'
    dom_html = ""
    if data.get("dominance"):
        d = dominance(data["dominance"]); res["_dominance"] = d
        rest = max(0.0, 100-d["btc_d"]-d["eth_d"]-d["others_d"]-d["stable_d"])
        tiles = [("BTC.D", "비트 도미", d["btc_d"], "#f7931a"), ("ETH.D", "이더 도미", d["eth_d"], "#8c9eff"),
                 ("OTHERS.D", "알트 도미", d["others_d"], "#2fd08a"), ("USDT.D+USDC.D", "스테이블 도미", d["stable_d"], "#3fc1c9")]
        dom_html = ('<h2><i>●</i> 도미넌스 <small>전체 시총 $' + f'{d["total_mcap"]/1e12:,.2f}' + '조</small></h2><div class="dom">'
                    + "".join(f'<div class="dt" style="border-top-color:{c}"><span>{a}</span><b style="color:{c}">{v:.2f}%</b><em>{k}</em></div>' for a, k, v, c in tiles)
                    + '</div><div class="bar">' + "".join(f'<i style="width:{v}%;background:{c}"></i>' for a, k, v, c in tiles)
                    + f'<i style="width:{rest}%;background:#2a3350"></i></div>')
    oc_html = ""; H = 1830
    oc = data.get("onchain")
    if oc and oc.get("realized"):
        H += 200; px = data["coins"]["BTC"]["usd"]
        def tile(label, en, val, note, color):
            if not val: return ""
            diff = (px/float(val)-1)*100
            pos = f"현재가가 {abs(diff):.1f}% {'위' if diff >= 0 else '아래'}"
            return (f'<div class="dt" style="border-top-color:{color}"><span>{label} <small>{en}</small></span>'
                    f'<b style="color:{color}">${float(val):,.0f}</b><em>{pos}{" · " + html.escape(note) if note else ""}</em></div>')
        oc_html = ('<h2><i>●</i> BTC 온체인 가격 <small>현재가 ' + usd_fmt(px) + '</small></h2><div class="dom">'
                   + tile("실현가격", "Realized Price", oc.get("realized"), oc.get("realized_note", ""), "#f7931a")
                   + tile("델타가격", "Delta Price", oc.get("delta"), oc.get("delta_note", ""), "#b48cff") + '</div>')
        res["_onchain"] = oc
    issues = "".join(f'<div class="is"><div class="n">{i+1}</div><div><b>{html.escape(re.sub(r"\[\[|\]\]|\*\*", "", t))}</b><p>{R(p)}</p></div></div>'
                     for i, (t, p) in enumerate(data["issues"][:5]))
    page = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:{H}px;background:#0b0f1a;color:#e9edf5;font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;padding:56px 56px 40px;position:relative;overflow:hidden}}
body:before{{content:"";position:absolute;right:-220px;top:-220px;width:640px;height:640px;border-radius:50%;background:radial-gradient(circle,#f7931a33,transparent 65%)}}
.top{{display:flex;justify-content:space-between;align-items:flex-end;border-bottom:2px solid #f7931a;padding-bottom:22px}}
.k{{font-size:22px;letter-spacing:6px;color:#f7931a;font-weight:700}}
.k span{{letter-spacing:2px;color:#9aa6bd;font-weight:500}}
h1{{font-size:68px;font-weight:900;line-height:1.1;margin-top:6px}}
.date{{text-align:right;font-size:24px;color:#9aa6bd;line-height:1.5}}
.date b{{color:#fff;font-size:30px}}
.mood{{margin:26px 0 22px;display:flex;gap:14px}}
.pill{{flex:1;background:#141a2b;border:1px solid #232c44;border-radius:14px;padding:12px 12px 12px 18px;display:flex;align-items:center;justify-content:space-between;gap:6px}}
.pi{{width:80px;height:80px;flex:none}}
.pill span{{display:block;font-size:18px;color:#8b97b0;white-space:nowrap}}
.pill b{{font-size:28px;white-space:nowrap}}
.red{{color:#ff5d6c}}.grn{{color:#2fd08a}}.org{{color:#f7931a}}
table{{width:100%;border-collapse:collapse;background:#111727;border-radius:16px;overflow:hidden}}
th{{font-size:19px;color:#8b97b0;font-weight:500;padding:13px 10px;background:#161d31;text-align:right}}
th:first-child,td:first-child{{text-align:left;padding-left:22px}}
td{{padding:15px 10px;text-align:right;font-size:26px;font-weight:700;border-top:1px solid #1e2740}}
td small{{display:block;font-size:19px;color:#8b97b0;font-weight:400}}
td.c{{font-size:32px;font-weight:900;white-space:nowrap}}
.ic{{display:inline-flex;width:46px;height:46px;border-radius:50%;align-items:center;justify-content:center;font-size:27px;font-weight:900;color:#fff;margin-right:14px;vertical-align:middle;font-family:"DejaVu Sans","Noto Sans CJK KR",sans-serif}}
.ic-BTC{{background:#f7931a}}.ic-ETH{{background:#5b6ee1}}.ic-SOL{{background:#8a4fe0}}.ic-XRP{{background:#3a4358;border:2px solid #9aa6bd}}
h2 small{{font-size:20px;color:#8b97b0;font-weight:400;margin-left:10px}}
.dom{{display:flex;gap:14px}}
.dt{{flex:1;background:#111727;border-top:4px solid;border-radius:12px;padding:14px 16px}}
.dt span{{display:block;font-size:20px;color:#aab4c8;font-weight:700}}
.dt span small{{font-size:16px;color:#8b97b0;font-weight:400;margin-left:6px}}
.dt b{{display:block;font-size:38px;font-weight:900;line-height:1.25}}
.dt em{{font-style:normal;font-size:19px;color:#8b97b0}}
.bar{{display:flex;height:14px;border-radius:7px;overflow:hidden;margin-top:14px}}
.bar i{{display:block;height:100%}}
td:last-child,th:last-child{{padding-right:22px}}
.os{{color:#ff5d6c}}.ob{{color:#2fd08a}}
h2{{font-size:30px;margin:30px 0 14px;font-weight:900}}
h2 i{{font-style:normal;color:#f7931a}}
.is{{display:flex;gap:18px;align-items:flex-start;background:#111727;border-left:5px solid #f7931a;border-radius:10px;padding:15px 20px;margin-bottom:11px}}
.n{{font-size:34px;font-weight:900;color:#f7931a;line-height:1.1;width:32px}}
.is b{{font-size:27px;display:block}}
.is p{{font-size:21px;color:#aab4c8;margin-top:3px}}
.num{{color:#ffb020;font-weight:700}}.nm{{color:#5cd6e0;font-weight:700}}
.pg{{position:absolute;right:56px;bottom:26px;font-size:24px;font-weight:700;color:#f7931a;letter-spacing:1px}}
.ft{{position:absolute;left:56px;right:230px;bottom:26px;font-size:17px;color:#6c7890;line-height:1.5}}
</style></head><body>
<div class="top"><div><div class="k">CRYPTO BRIEFING <span>· by Moni</span></div><h1>{html.escape(data["title"])}</h1></div>
<div class="date"><b>{html.escape(data["date"])}</b><br>{html.escape(data["asof"])}</div></div>
<div class="mood">{pills}</div>
<table><tr><th>코인</th><th>달러 / 원화</th><th>24시간</th><th>김프</th><th>RSI 일봉</th><th>주봉</th><th>월봉</th></tr>{rows}</table>
{dom_html}
{oc_html}
<h2><i>●</i> 오늘의 핵심 이슈</h2>{issues}
<div class="ft">가격: {html.escape(data.get('usd_source','OKX'))}(달러)·업비트(원화) / 김프: 환율 {fx:,.0f}원 적용 / RSI(14): 업비트 원화 차트 기준, 붉은색은 30 미만(과매도)·초록색은 70 초과(과매수) / 도미넌스: 시총 비중, OTHERS.D는 상위 10개 제외 · 투자 권유가 아닌 정보 제공용입니다.</div>
<div class="pg">{html.escape(data.get("page", "1/2 Page"))}</div>
</body></html>"""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); tmp.write(page); tmp.close()
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size=1080,{H}",
                    f"--screenshot={os.path.abspath(out_png)}", "file://"+tmp.name],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
