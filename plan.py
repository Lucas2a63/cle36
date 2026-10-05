"""Écrit plan.json : toutes les courses de la clé 36, réparties en tranches de charge égale.
Usage : python3 plan.py [nombre_de_tranches]"""
import json, sys

SEEDS = list(range(12))
COUT_MIN = {"mlp": 6.5, "cnn": 47.0}          # minutes par course sur un cœur (pilote), pour l'équilibrage


def taches():
    T = []
    # I — le cœur de la clé 33 : quatre régimes × trois mondes (perceptron, poids héréditaire, ancre ×30)
    for monde in ("fixe", "tourne", "degrade"):
        for regime in ("AUTO", "FIGE", "FRAIS", "ANCRE"):
            T += [dict(arch="mlp", regime=regime, monde=monde, valeur="SEL", c=30, seed=s) for s in SEEDS]
    # II — le cœur de la clé 35 : comment le poids atteint le réseau (perceptron, monde fixe, ancre ×c)
    for c in (1, 3, 10, 30, 100, 300, 1000):
        T += [dict(arch="mlp", regime="ANCRE", monde="fixe", valeur="IMP", c=c, seed=s) for s in SEEDS]
    for c in (1, 1000):                                   # SEL ×30 est la course ANCRE fixe de la partie I
        T += [dict(arch="mlp", regime="ANCRE", monde="fixe", valeur="SEL", c=c, seed=s) for s in SEEDS]
    for c in (30, 1000):
        T += [dict(arch="mlp", regime="ANCRE", monde="fixe", valeur="DIF", c=c, seed=s) for s in SEEDS]
    T += [dict(arch="mlp", regime="ANCRE", monde="fixe", valeur="RAM", c=1000, seed=s) for s in SEEDS]
    # III — les deux cœurs sur un réseau convolutif (monde fixe)
    for valeur, c in (("IMP", 1), ("IMP", 30), ("IMP", 1000), ("SEL", 1), ("SEL", 30), ("SEL", 1000), ("DIF", 1000)):
        T += [dict(arch="cnn", regime="ANCRE", monde="fixe", valeur=valeur, c=c, seed=s) for s in SEEDS]
    for regime in ("AUTO", "FRAIS"):
        T += [dict(arch="cnn", regime=regime, monde="fixe", valeur="SEL", c=30, seed=s) for s in SEEDS]
    return T


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    T = taches()
    ids = [f"{t['arch']}_{t['regime']}_{t['monde']}_{t['valeur']}_{t['c']:g}_s{t['seed']}" for t in T]
    assert len(set(ids)) == len(ids)
    # plus longues d'abord, chacune dans la tranche la moins chargée (ordre déterministe)
    ordre = sorted(range(len(T)), key=lambda i: (-COUT_MIN[T[i]["arch"]], i))
    charge = [0.0] * n
    tranches = {str(k + 1): [] for k in range(n)}
    for i in ordre:
        k = min(range(n), key=lambda j: (charge[j], j))
        tranches[str(k + 1)].append(T[i]); charge[k] += COUT_MIN[T[i]["arch"]]
    json.dump(dict(cle=36, courses=len(T), tranches=tranches), open("plan.json", "w"), ensure_ascii=False, indent=0)
    par = {}
    for t in T:
        par[t["arch"]] = par.get(t["arch"], 0) + 1
    print(f"{len(T)} courses {par} ; {n} tranches ; charge par tranche {min(charge) / 60:.1f}–{max(charge) / 60:.1f} h-cœur "
          f"(≈ {max(charge) / 60 / 4:.1f} h sur 4 cœurs) ; total {sum(charge) / 60:.0f} h-cœur")
