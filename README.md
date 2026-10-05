# Clé 36 — à l'échelle

Une population de 32 réseaux de neurones apprend CIFAR-10 par descente de gradient. À chaque
génération, ils sont classés, et les 8 derniers sont remplacés par des copies mutées des 8 premiers.
La classe fatale est le **chat** : rare dans le monde (3 %), l'oublier coûte 30 fois une erreur
ordinaire. C'est la classe la plus emmêlée du jeu (elle se confond d'abord avec le chien).

L'expérience rejoue, sur ces images naturelles et avec des réseaux plus grands, le cœur de deux
expériences antérieures faites sur MNIST et Fashion-MNIST :

- **sur quoi classer la population** — sa propre réussite (AUTO), une validation figée (FIGE), un
  échantillon neuf (FRAIS), ou un échantillon neuf visé sur la classe fatale et pondéré par le coût
  (ANCRE) — dans un monde fixe, un monde qui tourne, et un monde qui se dégrade (corruptions dans
  l'esprit de CIFAR-10-C) ;
- **comment le poids de la classe fatale atteint le réseau** — choisi par la seule sélection (SEL),
  imposé dans la perte dès le départ (IMP), imposé plus tard d'un coup (DIF) ou en rampe (RAM) —
  sur un perceptron et sur un réseau convolutif.

Les prédictions et la règle de décision ont été écrites **avant toute course** :
`PREENREGISTREMENT_36.md`. Son empreinte et celles du code sont dans `MANIFESTE.sha256`.

## Lancer

Rien que Python 3 et numpy.

```sh
sha256sum -c MANIFESTE.sha256            # rien n'a bougé depuis le pré-enregistrement
python3 controle_gradients.py            # les gradients des deux réseaux sont justes
python3 lancer.py --tranche 1            # une tranche du plan (4 processus par défaut)
```

Le plan complet (`plan.json`, écrit par `plan.py`) compte 396 courses réparties en 20 tranches
d'environ six heures-cœur chacune. Chaque tranche peut tourner dans sa propre session cloud :
les consignes des sessions sont dans `CLAUDE.md`.

## Fichiers

- `echelle.py` — le monde, les deux réseaux, la population, les régimes, le juge, les mesures.
- `lancer.py` — exécute une tranche, reprend là où elle s'était arrêtée.
- `plan.py`, `plan.json` — toutes les courses et leur répartition en tranches.
- `rassembler.py` — réunit les résultats poussés sur toutes les branches (et sert à la reprise d'une tranche).
- `verdict36.py` — applique la règle de décision, telle qu'écrite.
- `controle_gradients.py` — vérifie les gradients par différences finies.
- `donnees/` — CIFAR-10 réduit en 16×16 ; `preparer_donnees.py` dit comment, à partir de l'archive
  originale.

## Données

CIFAR-10 : Alex Krizhevsky, *Learning Multiple Layers of Features from Tiny Images*, 2009.
https://www.cs.toronto.edu/~kriz/cifar.html — réduit ici en 16×16 par moyenne des blocs 2×2.
