#!/usr/bin/env python3
"""Bunny mood icons (original SVG drawings based on the owner's two bunny characters).
bunny(style, mood) -> svg string.  style: "A" (white, oval eyes) | "B" (cream, round shiny eyes, nose, whiskers)
mood: extreme_fear | fear | neutral | greed | extreme_greed"""
import math

STYLE = {"A": dict(fur="#ffffff", line="#6b4a4a", ear="#f6a3ad", blush="#ffb3bd"),
         "B": dict(fur="#f6ead0", line="#b08a5a", ear="#e59a90", blush="#f5a9a4")}
EAR_ROT = {"extreme_fear": 56, "fear": 30, "neutral": 11, "greed": 9, "extreme_greed": 3}

def _drop(x, y, s, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><path d="M0-10Q-7 1-7 5.5A7 7 0 0 0 7 5.5Q7 1 0-10z" fill="#4fb3ff" stroke="#1f6fc2" stroke-width="1.2"/>'
            '<ellipse cx="-2.6" cy="4" rx="1.6" ry="2.6" fill="#fff" opacity=".85"/></g>')
def _heart(x, y, s):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0 4C-9-3-5-10 0-5.5C5-10 9-3 0 4z" fill="#e8372f" stroke="#a81f1a" stroke-width=".8"/>'
def _spark(x, y, s):
    return f'<path transform="translate({x} {y}) scale({s})" d="M0-8 2 -2 8 0 2 2 0 8-2 2-8 0-2-2z" fill="#ffd45a" stroke="#d99a00" stroke-width=".6"/>'

def _head(st):
    c = STYLE[st]; cx, cy, rx, ry = 60, 77, 45, 36
    if st == "B":   # soft round fluff
        pts = [(cx + rx*math.cos(a), cy + ry*math.sin(a)) for a in [i*2*math.pi/44 for i in range(44)]]
        out = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5.6" fill="{c["line"]}"/>' for x, y in pts)
        out += f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+1}" ry="{ry+1}" fill="{c["fur"]}"/>'
        out += "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{c["fur"]}"/>' for x, y in pts)
        out += f'<path d="M52 41q3-7 8-2q5-6 8 2" fill="{c["fur"]}" stroke="{c["line"]}" stroke-width="1.4"/>'
        return out
    n = 34; pts = []            # style A: spiky fur edge
    for i in range(n*2):
        a = i*math.pi/n; k = 1.0 if i % 2 == 0 else 0.90
        pts.append(f"{cx + rx*k*1.04*math.cos(a):.1f},{cy + ry*k*1.04*math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}" fill="{c["fur"]}" stroke="{c["line"]}" stroke-width="1.6" stroke-linejoin="round"/>'

def _ears(st, mood):
    c = STYLE[st]; r = EAR_ROT[mood]; out = ""
    for bx, sgn in ((41, -1), (79, 1)):
        out += (f'<g transform="rotate({sgn*r} {bx} 50)"><ellipse cx="{bx}" cy="29" rx="10.5" ry="22" fill="{c["fur"]}" stroke="{c["line"]}" stroke-width="1.8"/>'
                f'<ellipse cx="{bx}" cy="31" rx="5.2" ry="15" fill="{c["ear"]}"/></g>')
    return out

def _eyes(st, y=73, scale=1.0):
    if st == "B":
        r = 8.6*scale
        return "".join(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#16110f"/><circle cx="{x-2.6}" cy="{y-3}" r="{2.7*scale:.1f}" fill="#fff"/><circle cx="{x+2.6}" cy="{y+2.6}" r="{1.2*scale:.1f}" fill="#fff" opacity=".8"/>' for x in (44, 76))
    return "".join(f'<rect x="{x-5}" y="{y-10}" width="10" height="20" rx="5" fill="#111"/>' for x in (44, 76))

def _extras(st):
    c = STYLE[st]
    if st != "B": return "", ""
    nose = '<path d="M56.5 84h7q1 0 .4 1l-3 3.4q-.9 1-1.8 0l-3-3.4q-.6-1 .4-1z" fill="#ef8f8a" stroke="#c96d68" stroke-width=".8"/>'
    wh = f'<g stroke="{c["line"]}" stroke-width="1" stroke-linecap="round" opacity=".9"><path d="M26 82l-13-3M26 87l-13 2M94 82l13-3M94 87l13 2"/></g>'
    return nose, wh

def bunny(style="B", mood="neutral", cls="pi"):
    c = STYLE[style]; nose, wh = _extras(style)
    blush = f'<ellipse cx="31" cy="87" rx="8" ry="5" fill="{c["blush"]}"/><ellipse cx="89" cy="87" rx="8" ry="5" fill="{c["blush"]}"/>'
    my = 92 if style == "B" else 90      # mouth baseline
    K = 'stroke="#16110f" stroke-linecap="round" fill="none"'
    if mood == "extreme_fear":
        face = ('<path d="M28 58Q60 40 92 58L92 67Q60 52 28 67z" fill="#6f8ff0" opacity=".7"/>'
                '<g stroke="#3f5fd0" stroke-width="2.2" stroke-linecap="round"><path d="M42 52v10M51 49v11M60 48v11M69 49v11M78 52v10"/></g>'
                + "".join(f'<circle cx="{x}" cy="76" r="10.5" fill="#fff" stroke="#16110f" stroke-width="2.2"/><circle cx="{x}" cy="76" r="3" fill="#16110f"/>' for x in (44, 76))
                + f'<g {K} stroke-width="3"><path d="M33 64l14 5M87 64l-14 5"/></g>'
                '<path d="M40 87q-3 9-2 20q5 2 8 0q-1-10-1-20z" fill="#4fb3ff" stroke="#1f6fc2" stroke-width="1.2"/>'
                '<path d="M80 87q3 9 2 20q-5 2-8 0q1-10 1-20z" fill="#4fb3ff" stroke="#1f6fc2" stroke-width="1.2"/>'
                + nose + f'<path d="M50 {my+1}q2.5-4 5 0t5 0t5 0t5 0q-1 13-10 13t-10-13z" fill="#4a1f28" stroke="#16110f" stroke-width="1.6"/><ellipse cx="60" cy="{my+10}" rx="5" ry="2.6" fill="#ff8fa0"/>'
                + _drop(104, 44, 1.15, 25) + _drop(112, 64, .85, 25) + _drop(14, 52, .9, -25))
    elif mood == "fear":
        face = (blush + _eyes(style, 75, .92)
                + f'<g {K} stroke-width="3"><path d="M33 65l14-6M87 65l-14-6"/></g>'
                + nose + f'<path d="M48 {my+4}q3-5 6 0t6 0t6 0t6 0" {K} stroke-width="3"/>'
                + _drop(101, 50, 1.5, 18) + _drop(84, 60, .8, 0)
                + '<g stroke="#8fb7ff" stroke-width="2" stroke-linecap="round"><path d="M9 70l5 3M8 80h6M111 80h-5"/></g>')
    elif mood == "neutral":
        face = blush + _eyes(style) + nose + wh + f'<path d="M53 {my+3}h14" {K} stroke-width="3"/>'
    elif mood == "greed":
        face = (blush + f'<g {K} stroke-width="3.6"><path d="M36 77q8-12 16 0M68 77q8-12 16 0"/></g>' + nose + wh
                + f'<path d="M47 {my}q6.5 5 13 0q6.5 5 13 0q-2 13-13 13t-13-13z" fill="#4a1f28" stroke="#16110f" stroke-width="1.6"/><ellipse cx="60" cy="{my+9}" rx="6" ry="3" fill="#ff8fa0"/>'
                + _heart(104, 44, 1.25) + _heart(15, 56, .9))
    else:  # extreme_greed
        face = (blush + "".join(f'<circle cx="{x}" cy="74" r="11.5" fill="#ffc531" stroke="#b97800" stroke-width="2"/>'
                                f'<text x="{x}" y="80.5" font-size="18" font-weight="900" text-anchor="middle" fill="#7a4a00" font-family="DejaVu Sans,Arial,sans-serif">$</text>' for x in (44, 76))
                + nose + wh
                + f'<path d="M43 {my-1}q8.5 5 17 0q8.5 5 17 0q-2 18-17 18t-17-18z" fill="#4a1f28" stroke="#16110f" stroke-width="1.6"/><ellipse cx="60" cy="{my+12}" rx="8" ry="4" fill="#ff8fa0"/>'
                + f'<path d="M72 {my+13}q3 7 0 11q-4-3 0-11z" fill="#9fd8ff" stroke="#3f93d6" stroke-width=".9"/>'
                + _spark(105, 40, 1.3) + _spark(13, 46, 1.0) + _spark(109, 70, .75) + _heart(16, 74, .85))
    return (f'<svg class="{cls}" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">' + _ears(style, mood) + _head(style) + face + '</svg>')

if __name__ == "__main__":      # sample sheet html to stdout
    moods = [("extreme_fear", "극단적 공포"), ("fear", "공포"), ("neutral", "중립"), ("greed", "탐욕"), ("extreme_greed", "극단적 탐욕")]
    rows = ""
    for st, nm in (("B", "B안 · 두 번째 캐릭터 기준"), ("A", "A안 · 첫 번째 캐릭터 기준")):
        rows += f'<h2>{nm}</h2><div class="r">' + "".join(f'<div class="c">{bunny(st, m, "big")}<b>{l}</b><div class="sm">{bunny(st, m, "small")}<span>포스터 실제 크기</span></div></div>' for m, l in moods) + "</div>"
    print(f'''<!DOCTYPE html><html><head><meta charset="utf-8"><style>
body{{margin:0;width:1200px;box-sizing:border-box;background:#0b0f1a;color:#e9edf5;font-family:"Noto Sans CJK KR",sans-serif;padding:36px 40px}}
h1{{font-size:34px;margin:0 0 6px}}h2{{font-size:24px;color:#f7931a;margin:26px 0 12px}}
.r{{display:flex;gap:16px}}.c{{flex:1;background:#141a2b;border:1px solid #232c44;border-radius:16px;padding:14px 10px;text-align:center}}
.big{{width:190px;height:190px}}.c b{{display:block;font-size:22px;margin-top:2px}}
.sm{{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:10px;color:#8b97b0;font-size:15px}}.small{{width:74px;height:74px}}
</style></head><body><h1>공포·탐욕 지수 토끼 표정 샘플</h1>{rows}</body></html>''')
