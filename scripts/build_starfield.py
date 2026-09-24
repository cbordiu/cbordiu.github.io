#!/usr/bin/env python3
"""One-off: build src/data/starfield.json, the real bright-star field around η Car
behind the hero (Yale Bright Star Catalogue, V/50, via VizieR), with names for the
dwell-to-reveal labels (Bayer/Flamsteed from the BSC, IAU proper names from SIMBAD).
See docs/03-visual-design.md."""

import json
import math
import re
from pathlib import Path

import requests

RA0, DEC0 = 161.26477, -59.68443            # η Car (ICRS, Sesame)
X_EAST, X_WEST, HALF_H = 42.0, 30.0, 15.0    # field extent in degrees: η Car sits right of centre,
                                             # Crux and α/β Cen spread to the east (left)
VLIM = 5.8
OUT = Path(__file__).resolve().parent.parent / "src" / "data" / "starfield.json"

GREEK = dict(Alp="α", Bet="β", Gam="γ", Del="δ", Eps="ε", Zet="ζ", Eta="η", The="θ", Iot="ι", Kap="κ", Lam="λ",
             Mu="μ", Nu="ν", Xi="ξ", Omi="ο", Pi="π", Rho="ρ", Sig="σ", Tau="τ", Ups="υ", Phi="φ", Chi="χ",
             Psi="ψ", Ome="ω")
SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
# IAU (WGSN) names: fill SIMBAD gaps and pick the IAU form where SIMBAD lists several.
IAU = {"α¹ Cru": "Acrux", "β Cen": "Hadar", "α¹ Cen": "Rigil Kentaurus", "α² Cen": "Toliman", "β Cru": "Mimosa",
       "γ Cru": "Gacrux", "δ Cru": "Imai", "ε Cru": "Ginan", "β Car": "Miaplacidus", "ε Car": "Avior",
       "ι Car": "Aspidiske", "λ Vel": "Suhail", "δ Vel": "Alsephina", "γ² Vel": "Regor", "α Mus": None,
       "θ Car": None, "α Car": "Canopus"}


def bayer(name: str) -> str | None:
    """'Alp1Cru' -> 'α¹ Cru', ' 25Del CMa' -> 'δ CMa', '  43    Car' -> '43 Car'."""
    m = re.match(r"^\s*(\d*)\s*([A-Z][a-z]{1,2})?(\d)?\s*([A-Z][A-Za-z]{2})\s*$", name or "")
    if not m:
        return None
    flam, greek, sup, con = m.groups()
    if greek and greek in GREEK:
        return f"{GREEK[greek]}{(sup or '').translate(SUP)} {con}"
    return f"{flam} {con}" if flam else None


def proper_names(hrs: list[int]) -> dict[int, str]:
    ids = ",".join(f"'HR {h:>4}'" for h in hrs)
    q = (f"SELECT h.id AS hr, n.id AS name FROM ident AS h JOIN ident AS n ON h.oidref = n.oidref "
         f"WHERE h.id IN ({ids}) AND n.id LIKE 'NAME %'")
    r = requests.post("https://simbad.cds.unistra.fr/simbad/sim-tap/sync",
                      data={"request": "doQuery", "lang": "adql", "format": "json", "query": q}, timeout=120)
    r.raise_for_status()
    out: dict[int, str] = {}
    for hr, name in r.json()["data"]:
        out.setdefault(int(hr.split()[1]), name.removeprefix("NAME ").strip())
    return out


r = requests.get(
    "https://vizier.cds.unistra.fr/viz-bin/asu-tsv",
    params={"-source": "V/50/catalog", "-c": f"{RA0} {DEC0}", "-c.rd": 60,
            "-out": "_RAJ2000,_DEJ2000,Vmag,B-V,Name,HR,SpType", "Vmag": f"<{VLIM}", "-out.max": 5000},
    timeout=60,
)
r.raise_for_status()
rows = [l.split("\t") for l in r.text.splitlines() if l and not l.startswith("#")][3:]

a0, d0 = math.radians(RA0), math.radians(DEC0)
stars = []
for ra, dec, v, bv, name, hr, sp in rows:
    a, d = math.radians(float(ra)), math.radians(float(dec))
    cosc = math.sin(d0) * math.sin(d) + math.cos(d0) * math.cos(d) * math.cos(a - a0)
    # gnomonic projection; east to the left, as on the sky
    x = -math.degrees(math.cos(d) * math.sin(a - a0) / cosc)
    y = math.degrees((math.cos(d0) * math.sin(d) - math.sin(d0) * math.cos(d) * math.cos(a - a0)) / cosc)
    if not (-X_EAST <= x <= X_WEST) or abs(y) > HALF_H:
        continue
    stars.append({
        "x": round((x + X_EAST) / (X_EAST + X_WEST), 4),
        "y": round((HALF_H - y) / (2 * HALF_H), 4),
        "v": float(v),
        "bv": float(bv) if bv.strip() else 0.0,
        "hr": int(hr),
        "id": bayer(name),
        "sp": sp.strip(),
    })

names = proper_names([s["hr"] for s in stars])
for s in stars:
    iau = IAU.get(s["id"] or "", "")
    s["name"] = iau if iau is not None and iau != "" else (None if iau is None else names.get(s["hr"]))
    if not s["id"]:
        s["id"] = f"HR {s['hr']}"

stars.sort(key=lambda s: s["v"])
OUT.write_text(json.dumps({"centre": "eta Car", "centre_xy": [round(X_EAST / (X_EAST + X_WEST), 4), 0.5],
                           "vlim": VLIM, "stars": stars}, ensure_ascii=False, separators=(",", ":")) + "\n")
print(f"{len(stars)} stars, {sum(bool(s['name']) for s in stars)} with proper names -> {OUT}")
