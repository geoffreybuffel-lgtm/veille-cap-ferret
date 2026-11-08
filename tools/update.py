"""Mise à jour hebdomadaire de data.json à partir d'un nouveau relevé.

Usage : python3 tools/update.py releve/ AAAA-MM-JJ
Le dossier releve/ contient un CSV par agence, avec l'en-tête :
    agence,titre,type,secteur,prix,surface,chambres,terrain,ref,url,image
(prix vide = prix sur demande ; type = V, VP, A ou T ; url = lien de l'annonce, sert d'identifiant).
Les biens de l'Agence du Cap ont agence = "Agence du Cap".

Effets :
- bien jamais vu        -> ajouté, événement "nouveau"
- prix changé           -> historique complété, événement "baisse" ou "hausse"
- bien actif absent     -> statut "retiré" (vendu ou mandat retiré), événement "retire"
- bien retiré revenu    -> statut "actif", événement "remis"
Une agence dont le relevé est vide est ignorée (site en panne) : ses biens ne sont pas marqués retirés.
"""
import csv, json, sys, glob, os

LEGE = {"lège", "lege", "lège bourg"}

def num(v):
    v = (v or "").strip().replace(" ", "").replace(" ", "")
    if not v:
        return None
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except ValueError:
        return None

def main(folder, date, path="data.json"):
    data = json.load(open(path, encoding="utf-8"))
    by_id = {b["id"]: b for b in data["biens"]}
    seen, agences_ok, ev = set(), set(), []
    for f in sorted(glob.glob(os.path.join(folder, "*.csv"))):
        rows = list(csv.DictReader(open(f, encoding="utf-8")))
        for r in rows:
            url = (r.get("url") or "").strip()
            if not url or (r.get("secteur") or "").strip().lower() in LEGE:
                continue
            ag = r["agence"].strip()
            agences_ok.add(ag)
            nous = ag == "Agence du Cap"
            bid = ("AC-" + url.rstrip("/").split("/")[-1]) if nous else url
            seen.add(bid)
            prix = num(r.get("prix"))
            champs = {k: num(r.get(k)) for k in ("surface", "chambres", "terrain")}
            b = by_id.get(bid)
            if b is None:
                b = {"id": bid, "agence": ag, "nous": nous, "titre": r.get("titre", "").strip(),
                     "type": r.get("type", "V").strip() or "V", "secteur": (r.get("secteur") or "").strip() or None,
                     "prix": prix, **champs, "url": url, "image": (r.get("image") or "").strip() or None,
                     "first_seen": date, "last_seen": date, "statut": "actif", "hist": [[date, prix]]}
                data["biens"].append(b); by_id[bid] = b
                ev.append({"date": date, "type": "nouveau", "id": bid, "prix": prix})
                continue
            if b["statut"] != "actif":
                b["statut"] = "actif"; b.pop("retire_le", None)
                ev.append({"date": date, "type": "remis", "id": bid, "prix": prix})
            if prix != b.get("prix") and prix is not None and b.get("prix") is not None:
                ev.append({"date": date, "type": "baisse" if prix < b["prix"] else "hausse",
                           "id": bid, "avant": b["prix"], "prix": prix})
            if prix != b.get("prix"):
                b["hist"].append([date, prix])
            b["prix"] = prix
            for k, v in champs.items():
                if v is not None:
                    b[k] = v
            img = (r.get("image") or "").strip()
            if img:
                b["image"] = img
            if (r.get("secteur") or "").strip() and not b.get("secteur"):
                b["secteur"] = r["secteur"].strip()
            b["last_seen"] = date
    for b in data["biens"]:
        if b["statut"] == "actif" and b["id"] not in seen and b["agence"] in agences_ok:
            b["statut"] = "retiré"; b["retire_le"] = date
            ev.append({"date": date, "type": "retire", "id": b["id"], "prix": b.get("prix")})
    data["evenements"] = ev + data.get("evenements", [])
    data["maj"] = date
    if date not in data["releves"]:
        data["releves"].append(date)
    json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    manquantes = sorted({a["nom"] for a in data["agences"]} - agences_ok)
    print(f"{len(ev)} événements ; agences sans relevé : {', '.join(manquantes) or 'aucune'}")
    for t in ("nouveau", "baisse", "hausse", "retire", "remis"):
        print(t, sum(e["type"] == t for e in ev))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
