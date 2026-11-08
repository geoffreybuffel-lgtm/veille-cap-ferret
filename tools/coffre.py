"""Chiffrement des données de la veille (AES-256-GCM, clé dérivée du mot de passe par PBKDF2-SHA256).

    python3 tools/coffre.py ouvrir    # data.enc.json -> data.json (en clair, jamais commité)
    python3 tools/coffre.py fermer    # data.json -> data.enc.json (à commiter)

Le mot de passe est lu dans la variable d'environnement VEILLE_MDP.
La page index.html déchiffre data.enc.json dans le navigateur avec le même mot de passe.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 250_000
b64 = lambda b: base64.b64encode(b).decode()

def cle(mdp, sel):
    return PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=sel, iterations=ITER).derive(mdp.encode())

def fermer(mdp, src="data.json", dst="data.enc.json"):
    clair = open(src, "rb").read()
    json.loads(clair)  # refuse un fichier abîmé
    sel, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(cle(mdp, sel)).encrypt(iv, clair, None)
    json.dump({"v": 1, "iter": ITER, "sel": b64(sel), "iv": b64(iv), "ct": b64(ct)}, open(dst, "w"))

def ouvrir(mdp, src="data.enc.json", dst="data.json"):
    e = json.load(open(src))
    sel, iv, ct = (base64.b64decode(e[k]) for k in ("sel", "iv", "ct"))
    clair = AESGCM(cle(mdp, sel)).decrypt(iv, ct, None)
    open(dst, "wb").write(clair)

if __name__ == "__main__":
    mdp = os.environ.get("VEILLE_MDP")
    if not mdp:
        sys.exit("VEILLE_MDP manquant")
    {"ouvrir": ouvrir, "fermer": fermer}[sys.argv[1]](mdp)
    print("ok")
