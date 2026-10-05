"""Rassemble les résultats poussés sur toutes les branches du dépôt.

  python3 rassembler.py          toutes les tranches ; écrit resultats/tranche_K.json et resultats/bilan.txt
  python3 rassembler.py K        la seule tranche K (reprise d'une tranche interrompue)

À lancer après : git fetch origin '+refs/heads/*:refs/remotes/origin/*'
Chaque session pousse sur sa propre branche ; les courses d'une tranche trouvées sur plusieurs
branches sont réunies (une course est déterministe à sa graine près : n'importe quel exemplaire vaut).
"""
import json, os, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
plan = json.load(open(os.path.join(ICI, "plan.json")))
os.makedirs(os.path.join(ICI, "resultats"), exist_ok=True)


def ident(t):
    return f"{t['arch']}_{t['regime']}_{t['monde']}_{t['valeur']}_{t['c']:g}_s{t['seed']}"


def branches():
    r = subprocess.run(["git", "for-each-ref", "--format=%(refname)", "refs/remotes/"],
                       capture_output=True, text=True, cwd=ICI)
    return [b for b in r.stdout.split() if not b.endswith("/HEAD")]


def reunir(k, bs):
    chemin = os.path.join(ICI, "resultats", f"tranche_{k}.json")
    out = json.load(open(chemin)) if os.path.exists(chemin) else {}
    for b in bs:
        r = subprocess.run(["git", "show", f"{b}:resultats/tranche_{k}.json"], capture_output=True, cwd=ICI)
        if r.returncode == 0:
            try:
                for i, v in json.loads(r.stdout).items():
                    out.setdefault(i, v)
            except ValueError:
                pass
    if out:
        tmp = chemin + ".tmp"
        json.dump(out, open(tmp, "w")); os.replace(tmp, chemin)
    return out


if __name__ == "__main__":
    bs = branches()
    ks = [sys.argv[1]] if len(sys.argv) > 1 else sorted(plan["tranches"], key=int)
    lignes, total, faites = [], 0, 0
    for k in ks:
        taches = plan["tranches"][k]
        out = reunir(k, bs)
        n = sum(ident(t) in out for t in taches)
        total += len(taches); faites += n
        etat = "complète" if n == len(taches) else ("absente" if n == 0 else "incomplète")
        lignes.append(f"tranche {k:>2} : {n:>2}/{len(taches)}  {etat}")
    lignes.append(f"TOTAL : {faites}/{total} courses ({len(bs)} branches lues)")
    if len(ks) > 1:
        open(os.path.join(ICI, "resultats", "bilan.txt"), "w").write("\n".join(lignes) + "\n")
    print("\n".join(lignes))
