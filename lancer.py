"""Exécute une tranche du plan : python3 lancer.py --tranche K [--processus 4]

Chaque course tourne dans son propre processus, sur un seul fil de calcul. Les résultats s'écrivent
au fur et à mesure dans resultats/tranche_K.json (écriture atomique). Une course déjà présente dans
ce fichier n'est pas refaite : relancer la même commande reprend là où l'on s'était arrêté.
"""
import os
for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[v] = "1"
import argparse, json, multiprocessing as mp, sys, time

ICI = os.path.dirname(os.path.abspath(__file__))


def ident(t):
    return f"{t['arch']}_{t['regime']}_{t['monde']}_{t['valeur']}_{t['c']:g}_s{t['seed']}"


def une_course(t):
    import echelle
    t0 = time.time()
    r = echelle.course(t["arch"], t["regime"], t["monde"], t["valeur"], float(t["c"]), int(t["seed"]),
                       int(t.get("gens", echelle.GENS)))
    r["duree"] = time.time() - t0
    r["tache"] = t
    return ident(t), r


def ecrire(chemin, out):
    tmp = chemin + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f)
    os.replace(tmp, chemin)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tranche", required=True)
    ap.add_argument("--processus", type=int, default=min(4, os.cpu_count() or 1))
    ap.add_argument("--plan", default=os.path.join(ICI, "plan.json"))
    a = ap.parse_args()
    plan = json.load(open(a.plan))
    taches = plan["tranches"][str(a.tranche)]
    os.makedirs(os.path.join(ICI, "resultats"), exist_ok=True)
    chemin = os.path.join(ICI, "resultats", f"tranche_{a.tranche}.json")
    out = json.load(open(chemin)) if os.path.exists(chemin) else {}
    reste = [t for t in taches if ident(t) not in out]
    print(f"tranche {a.tranche} : {len(taches)} courses, {len(taches) - len(reste)} déjà faites, "
          f"{len(reste)} à faire, sur {a.processus} processus", flush=True)
    t0 = time.time()
    if reste:
        with mp.get_context("spawn").Pool(a.processus, maxtasksperchild=1) as pool:
            for k, r in pool.imap_unordered(une_course, reste):
                out[k] = r
                ecrire(chemin, out)
                fait = sum(ident(t) in out for t in taches)
                print(f"  {k:<34} fait en {r['duree'] / 60:5.1f} min   [{fait}/{len(taches)}]   "
                      f"écoulé {(time.time() - t0) / 60:5.1f} min", flush=True)
    fait = sum(ident(t) in out for t in taches)
    if fait == len(taches):
        print(f"TRANCHE {a.tranche} TERMINÉE — {fait} courses dans resultats/tranche_{a.tranche}.json", flush=True)
    else:
        print(f"tranche {a.tranche} incomplète : {fait}/{len(taches)}", flush=True)
        sys.exit(1)
