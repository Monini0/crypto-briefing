#!/usr/bin/env python3
"""Issue deep-dive poster (2nd poster). Usage: python3 tools/build_issue.py issue.json out.png
issue.json:
{
 "date": "2026.11.19 (목)", "tag": "이슈 3",                      (tag optional)
 "title": "두 줄 이내 제목", "lead": "2~3문장 요약",
 "stats": [["라벨", "큰 숫자", "보조 설명"], ... 3개],
 "sections": [{"h": "소제목", "bullets": ["짧은 문장", ...2~3개]}, ... 3개],
 "note": {"h": "체크 포인트", "bullets": ["...", "..."]},          (optional, 강조 박스)
 "sources": "CoinDesk, FXStreet 등 보도 종합"
}
글 분량 기준: lead 110자 이내, bullet 한 개 45자 이내, 전체 bullet 10개 이내.
강조 표기(반드시 사용): lead·bullets·note 문장 안에서
  [[...]] = 숫자·금액·비율·날짜 (주황색)   예: "공모가보다 약 [[24%]] 높게 거래"
  **...** = 기업·코인·기관·상품 등 명칭 (하늘색)  예: "**OKX** 상장 전 선물"
한 문장에 1~3곳만 강조한다. 우측 하단에는 "2/2 Page"가 자동으로 들어간다.
"""
import json, sys, subprocess, html, os, tempfile
import re
E = html.escape
def R(t):
    """escape + highlight markup"""
    t = E(t)
    t = re.sub(r"\[\[(.+?)\]\]", r'<b class="num">\1</b>', t)
    return re.sub(r"\*\*(.+?)\*\*", r'<b class="nm">\1</b>', t)

def main():
    d = json.load(open(sys.argv[1], encoding="utf-8")); out = sys.argv[2]
    stats = "".join(f'<div class="st"><span>{E(a)}</span><b>{E(b)}</b><em>{E(c)}</em></div>' for a, b, c in d.get("stats", [])[:3])
    secs = "".join(f'<div class="sec"><h3><i>{i+1}</i>{E(s["h"])}</h3><ul>' + "".join(f"<li>{R(x)}</li>" for x in s["bullets"]) + "</ul></div>"
                   for i, s in enumerate(d["sections"]))
    note = ""
    if d.get("note"):
        note = f'<div class="note"><h4>⚠ {E(d["note"]["h"])}</h4><ul>' + "".join(f"<li>{R(x)}</li>" for x in d["note"]["bullets"]) + "</ul></div>"
    H = int(d.get("height", 1830))
    tag = f'<span class="tag">{E(d["tag"])}</span>' if d.get("tag") else ""
    page = f"""<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:1080px;height:{H}px;background:#0b0f1a;color:#e9edf5;font-family:"Noto Sans CJK KR","Noto Sans KR",sans-serif;padding:56px 56px 40px;position:relative;overflow:hidden}}
body:before{{content:"";position:absolute;left:-240px;top:-240px;width:680px;height:680px;border-radius:50%;background:radial-gradient(circle,#f7931a2e,transparent 65%)}}
.top{{display:flex;justify-content:space-between;align-items:center;position:relative}}
.k{{font-size:22px;letter-spacing:6px;color:#f7931a;font-weight:700}}
.k span{{letter-spacing:2px;color:#9aa6bd;font-weight:500}}
.date{{font-size:24px;color:#9aa6bd}}
.tag{{display:inline-block;margin-top:44px;background:#f7931a;color:#0b0f1a;font-weight:900;font-size:22px;padding:6px 16px;border-radius:8px}}
h1{{font-size:70px;font-weight:900;line-height:1.22;margin-top:18px;letter-spacing:-1px;word-break:keep-all}}
.lead{{font-size:29px;line-height:1.6;color:#c6cee0;margin-top:26px;padding-left:22px;border-left:5px solid #f7931a;word-break:keep-all}}
.stats{{display:flex;gap:14px;margin-top:36px}}
.st{{flex:1;background:#141a2b;border:1px solid #232c44;border-radius:14px;padding:18px 20px}}
.st span{{display:block;font-size:21px;color:#8b97b0}}
.st b{{display:block;font-size:44px;font-weight:900;color:#f7931a;line-height:1.3;white-space:nowrap}}
.st em{{font-style:normal;font-size:19px;color:#aab4c8}}
.sec{{margin-top:34px}}
h3{{font-size:34px;font-weight:900;display:flex;align-items:center;gap:14px}}
h3 i{{font-style:normal;display:inline-flex;width:44px;height:44px;border-radius:50%;background:#f7931a;color:#0b0f1a;align-items:center;justify-content:center;font-size:26px}}
ul{{list-style:none;margin-top:12px}}
li{{font-size:27px;line-height:1.5;color:#d5dbea;padding:7px 0 7px 34px;position:relative;word-break:keep-all}}
li:before{{content:"";position:absolute;left:10px;top:25px;width:9px;height:9px;border-radius:50%;background:#f7931a}}
.note{{margin-top:36px;background:#1a1620;border:1px solid #5a3a1a;border-radius:14px;padding:20px 24px}}
.note h4{{font-size:27px;color:#ffb454;font-weight:900}}
.note li{{font-size:25px}}.note li:before{{background:#ffb454}}
.num{{color:#ffb020;font-weight:700}}.nm{{color:#5cd6e0;font-weight:700}}
.pg{{position:absolute;right:56px;bottom:26px;font-size:24px;font-weight:700;color:#f7931a;letter-spacing:1px}}
.ft{{position:absolute;left:56px;right:230px;bottom:26px;font-size:17px;color:#6c7890;line-height:1.5}}
</style></head><body>
<div class="top"><div class="k">ISSUE DEEP DIVE <span>· by Moni</span></div><div class="date">{E(d["date"])}</div></div>
{tag}<h1>{E(d["title"])}</h1>
<p class="lead">{R(d["lead"])}</p>
<div class="stats">{stats}</div>
{secs}{note}
<div class="ft">출처: {E(d.get("sources",""))} · 투자 권유가 아닌 정보 제공용입니다.</div>
<div class="pg">{E(d.get("page", "2/2 Page"))}</div>
</body></html>"""
    tmp = tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8"); tmp.write(page); tmp.close()
    subprocess.run(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size=1080,{H}",
                    f"--screenshot={os.path.abspath(out)}", "file://"+tmp.name],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if __name__ == "__main__":
    main()
