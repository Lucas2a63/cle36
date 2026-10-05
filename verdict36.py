"""Applique la règle de décision de PREENREGISTREMENT_36.md, telle qu'écrite.
Lit resultats/tranche_*.json ; écrit resultats/verdicts36.json. Usage : python3 verdict36.py"""
import glob, json, os
import numpy as np

ICI = os.path.dirname(os.path.abspath(__file__))
R = {}
for f in sorted(glob.glob(os.path.join(ICI, "resultats", "tranche_*.json"))):
    R.update(json.load(open(f)))
G = 119
MONDES = ("fixe", "tourne", "degrade")
V = {}
S = list(range(12))            # graines de la comparaison en cours (fixées par dispo)


def cle(cd, s):
    arch, regime, monde, valeur, c = cd
    return f"{arch}_{regime}_{monde}_{valeur}_{c:g}_s{s}"


def dispo(*cds):
    """Graines complètes pour toutes les conditions de la comparaison (au moins 3)."""
    global S
    S = [s for s in range(12) if all(cle(cd, s) in R for cd in cds)]
    return len(S) >= 3


def J(cd, m, g=G):
    return np.array([[x[m] for x in R[cle(cd, s)]["juge"] if x["g"] == g][0] for s in S])


def T(cd, m, g=G):
    return np.array([R[cle(cd, s)]["tr"][g][m] for s in S])


def F(cd, m):
    return np.array([R[cle(cd, s)]["fin"][m] for s in S])


def points(cd):
    return [x["g"] for x in R[cle(cd, S[0])]["juge"]]


def t_app(d):
    d = np.asarray(d, float)
    se = d.std(ddof=1) / np.sqrt(len(d))
    return float(d.mean()), (float(d.mean() / se) if se > 0 else float(np.sign(d.mean()) * np.inf))


def note(nom, **kw):
    kw["graines"] = len(S)
    V[nom] = kw


def signe(nom, d, s=+1):
    """Écart apparié : confirmé si du signe prédit avec |t| > 2, démenti si significatif dans l'autre sens."""
    m, t = t_app(d)
    note(nom, ecart=m, t=t, verdict=("confirmé" if np.sign(t) == s else "démenti") if abs(t) > 2 else "indécidable")


def seuil_bas(nom, d, seuil, garde):
    """Prédit : écart moyen ≤ seuil (négatif) avec t < −2 ; démenti si l'écart moyen dépasse `garde`."""
    m, t = t_app(d)
    note(nom, ecart=m, t=t, verdict="confirmé" if (m <= seuil and t < -2) else ("démenti" if m > garde else "indécidable"))


def proche(nom, d, tol):
    """Prédit : pas d'écart durable, |moyenne| < tol ; démenti si |moyenne| ≥ tol avec |t| > 2."""
    m, t = t_app(d)
    note(nom, ecart=m, t=t, verdict="confirmé" if abs(m) < tol else ("démenti" if abs(t) > 2 else "indécidable"))


def fraction(nom, x, borne, sens):
    m = float(np.mean(x))
    note(nom, fraction=m, verdict="confirmé" if (m >= borne if sens > 0 else m <= borne) else "démenti")


def mensonge(cd, g=G):
    """Note affichée du meilleur − la même grandeur lue par le juge sur ce réseau."""
    return J(cd, "note_b", g) - J(cd, "V30_b" if cd[1] == "ANCRE" else "simple_b", g)


def mensonge_pop(cd, g):
    return T(cd, "note_moy", g) - J(cd, "V30" if cd[1] == "ANCRE" else "simple", g)


def vainqueur(nom, cd):
    m, t = t_app(mensonge(cd))
    note(nom, ecart=m, t=t, verdict="confirmé" if (m > 0.03 and t > 2) else ("démenti" if m <= 0.03 else "indécidable"))


def population(nom, cd):
    pire = max(abs(mensonge_pop(cd, g).mean()) for g in points(cd))
    note(nom, pire=float(pire), verdict="confirmé" if pire < 0.03 else "démenti")


def stress(cd):
    return np.array([np.mean([v["V30"] for k, v in R[cle(cd, s)]["fin"]["rob"].items() if k != "propre"]) for s in S])


def ecart_front(cd, ref):
    """A_ord(cd) − A_ord que donne la population ref (même graine), rereglée par le seul biais du chat."""
    out = []
    for s in S:
        a, b = R[cle(cd, s)], R[cle(ref, s)]
        cible = [x for x in a["juge"] if x["g"] == G][0]
        rf, ao = np.array(b["fin"]["Rf"]), np.array(b["fin"]["Ao"])
        o = np.argsort(rf, kind="stable")
        out.append(cible["Aord"] - float(np.interp(cible["Rf"], rf[o], ao[o])))
    return np.array(out)


def P(regime, monde, arch="mlp"):
    return (arch, regime, monde, "SEL", 30)


def Q(arch, valeur, c):
    return (arch, "ANCRE", "fixe", valeur, c)


# =============================================================== A — la clé 33 à l'échelle (perceptron)
for monde in MONDES:
    au, fi, fr, an = (P(r, monde) for r in ("AUTO", "FIGE", "FRAIS", "ANCRE"))
    nomme = {au: "AUTO", fi: "FIGE", fr: "FRAIS", an: "ANCRE"}
    for x in (fi, fr, an):
        if dispo(au, x):
            signe(f"A1 {monde} mensonge AUTO>{nomme[x]}", mensonge(au) - mensonge(x))
    if dispo(au):
        m = float(mensonge(au).mean())
        note(f"A1 {monde} mensonge AUTO>0,10", ecart=m, verdict="confirmé" if m > 0.10 else "démenti")
    if monde == "fixe":
        if dispo(fi):
            signe("A2 fixe mensonge FIGE>0", mensonge(fi))
    elif dispo(fr, fi):
        signe(f"A2 {monde} verite FRAIS>FIGE", J(fr, "V30_b") - J(fi, "V30_b"))
    for x in (fr, an):
        if dispo(x):
            vainqueur(f"A3a {monde} {nomme[x]} vainqueur>0,03", x)
            population(f"A3b {monde} {nomme[x]} population<0,03", x)
    for x in (fi, fr):
        if dispo(au, x):
            signe(f"A4 {monde} chat AUTO<{nomme[x]}", J(x, "Rf_b") - J(au, "Rf_b"))
    for x in (au, fi, fr):
        if dispo(an, x):
            signe(f"A4 {monde} chat ANCRE>{nomme[x]}", J(an, "Rf_b") - J(x, "Rf_b"))
    if dispo(an):
        signe(f"A5 {monde} poids ANCRE>1", T(an, "lpf"))
    for x in (au, fi, fr):
        if dispo(an, x):
            signe(f"A5 {monde} poids ANCRE>{nomme[x]}", T(an, "lpf") - T(x, "lpf"))
    for x in (fr, an):
        if monde != "fixe" and dispo(au, x):
            signe(f"A6 {monde} eps AUTO>{nomme[x]}", T(au, "eps") - T(x, "eps"))
        if monde == "fixe" and dispo(x):
            signe(f"A7 fixe eps descend {nomme[x]}", T(x, "eps", 0) - T(x, "eps"))
    for x in (au, fi, fr):
        if dispo(an, x):
            signe(f"A8 {monde} verite ANCRE>{nomme[x]}", J(an, "V30_b") - J(x, "V30_b"))
            signe(f"A9 {monde} stress ANCRE>{nomme[x]}", stress(an) - stress(x))


# =============================================================== B et C — la clé 35 à l'échelle
def bloc(arch, X):
    imp = lambda c: Q(arch, "IMP", c)
    sel = lambda c: Q(arch, "SEL", c)
    if dispo(imp(1000), imp(30)):
        seuil_bas(f"{X}1 IMP A_ord x1000-x30 <= -3 pts", J(imp(1000), "Aord") - J(imp(30), "Aord"), -0.03, -0.01)
    if arch == "mlp" and dispo(imp(300), imp(30)):
        seuil_bas(f"{X}1b IMP A_ord x300-x30 <= -10 pts", J(imp(300), "Aord") - J(imp(30), "Aord"), -0.10, -0.03)
    if dispo(imp(1000), imp(30), sel(1000), sel(30)):
        signe(f"{X}2 le cliquet protege", (J(imp(1000), "Aord") - J(imp(30), "Aord"))
              - (J(sel(1000), "Aord") - J(sel(30), "Aord")), -1)
    if dispo(imp(30), imp(1)):
        signe(f"{X}3 IMP V30 x30>x1", J(imp(30), "V30") - J(imp(1), "V30"))
    if arch == "cnn" and dispo(imp(30), imp(1000)):
        signe(f"{X}3 IMP V30 x30>x1000", J(imp(30), "V30") - J(imp(1000), "V30"))
    grille = (1, 3, 10, 30, 100, 300, 1000)
    if arch == "mlp" and dispo(*[imp(c) for c in grille]):
        moy = {str(c): float(J(imp(c), "V30").mean()) for c in grille}
        best = int(max(moy, key=moy.get))
        note(f"{X}3b meilleur point de la grille au-dessus de x30", V30=moy, meilleur=best,
             verdict="confirmé" if best > 30 else "démenti")
    if dispo(imp(1000)):
        fraction(f"{X}4 IMP x1000 gele au depart (g0)", J(imp(1000), "gel", 0), 0.5, +1)
    if dispo(sel(1000)):
        pire = max(float(J(sel(1000), "gel", g).mean()) for g in (0, 1, 2, 4, 8))
        note(f"{X}4 SEL x1000 pas de gel au depart", pire=pire, verdict="confirmé" if pire <= 0.05 else "démenti")
    for valeur in ("DIF", "RAM"):
        if (valeur == "DIF" or arch == "mlp") and dispo(Q(arch, valeur, 1000)):
            fraction(f"{X}5 {valeur} x1000 gele a g35", J(Q(arch, valeur, 1000), "gel", 35), 0.5, +1)
    if dispo(Q(arch, "DIF", 1000), imp(1000)):
        proche(f"{X}5 A_ord DIF x1000 = IMP x1000 (+-3 pts)", J(Q(arch, "DIF", 1000), "Aord") - J(imp(1000), "Aord"), 0.03)
    if arch == "mlp" and dispo(Q(arch, "DIF", 30), imp(30)):
        proche(f"{X}5 V30 DIF x30 = IMP x30 (+-2 pts)", J(Q(arch, "DIF", 30), "V30") - J(imp(30), "V30"), 0.02)
    if dispo(imp(1000), imp(30)):
        seuil_bas(f"{X}6 sonde x1000-x30 <= -5 pts", F(imp(1000), "sonde") - F(imp(30), "sonde"), -0.05, -0.05)
        seuil_bas(f"{X}7 front x1000 vs x30 <= -2 pts", ecart_front(imp(1000), imp(30)), -0.02, -0.02)
        signe(f"{X}8 dimension x1000<x30", F(imp(1000), "PR") - F(imp(30), "PR"), -1)


bloc("mlp", "B")
bloc("cnn", "C")

# C9 — le cœur de la clé 33 sur le réseau convolutif (monde fixe)
au, fr, an = (P(r, "fixe", "cnn") for r in ("AUTO", "FRAIS", "ANCRE"))
nomme = {au: "AUTO", fr: "FRAIS", an: "ANCRE"}
if dispo(au):
    m = float(mensonge(au).mean())
    note("C9 mensonge AUTO>0,10", ecart=m, verdict="confirmé" if m > 0.10 else "démenti")
for x in (fr, an):
    if dispo(au, x):
        signe(f"C9 mensonge AUTO>{nomme[x]}", mensonge(au) - mensonge(x))
    if dispo(x):
        vainqueur(f"C9 {nomme[x]} vainqueur>0,03", x)
        population(f"C9 {nomme[x]} population<0,03", x)
for x in (au, fr):
    if dispo(an, x):
        signe(f"C9 chat ANCRE>{nomme[x]}", J(an, "Rf_b") - J(x, "Rf_b"))
        signe(f"C9 verite ANCRE>{nomme[x]}", J(an, "V30_b") - J(x, "V30_b"))

os.makedirs(os.path.join(ICI, "resultats"), exist_ok=True)
json.dump(V, open(os.path.join(ICI, "resultats", "verdicts36.json"), "w"), indent=1, ensure_ascii=False)
compte = {}
for k, v in V.items():
    compte[v["verdict"]] = compte.get(v["verdict"], 0) + 1
    print(f"{k:<46} {v['verdict']:<12} n={v['graines']:<3}"
          + " ".join(f"{kk}={vv:+.4f}" for kk, vv in v.items() if isinstance(vv, float)))
print(compte, f"— {len(R)} courses lues")
