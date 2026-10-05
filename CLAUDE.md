# Consignes pour les sessions cloud — clé 36

Ce dépôt contient une expérience **pré-enregistrée** (`PREENREGISTREMENT_36.md` ; empreintes du
code, du plan et des données dans `MANIFESTE.sha256`). Chaque session cloud exécute **une tranche**
du plan (`plan.json`), telle qu'écrite, et pousse ses résultats sur **sa propre branche de travail**.
Rien d'autre : pas d'analyse, pas de modification, pas d'initiative.

## Si le message dit « Tranche K »

0. **Données envoyées à plat** : si les données ne sont pas dans `donnees/` mais à la racine du dépôt
   (envoi par un navigateur), reconstitue-les sans toucher aux fichiers du dépôt :
   - en morceaux (`cifar16_a.npz.part1`, `.part2`…) :
     `mkdir -p donnees && cat cifar16_a.npz.part* > donnees/cifar16_a.npz && cat cifar16_b.npz.part* > donnees/cifar16_b.npz && cp cifar16_t.npz donnees/`
   - entières (`cifar16_a.npz`…) : `mkdir -p donnees && cp cifar16_*.npz donnees/`

   Ce dossier `donnees/` reste local et ne doit jamais être commité.
1. **Vérifier que rien n'a bougé** : `sha256sum -c MANIFESTE.sha256`. Si une ligne échoue, arrête-toi
   et signale-le, sans rien lancer.
2. **numpy** : `python3 -c "import numpy; print(numpy.__version__)"`. S'il manque :
   `pip install numpy` (si pip refuse : `pip install --break-system-packages numpy`).
3. **Contrôle** : `python3 controle_gradients.py` doit afficher « bon » deux fois.
4. **Reprise éventuelle** : `git fetch origin '+refs/heads/*:refs/remotes/origin/*'` puis
   `python3 rassembler.py K`. Si une session précédente avait commencé la tranche K, ses courses
   finies sont récupérées et ne seront pas refaites.
5. **Lancer en arrière-plan** :
   `nohup python3 lancer.py --tranche K > journal_K.log 2>&1 &`
   La première ligne du journal dit combien de courses sont à faire. Une tranche dure de une à trois
   heures environ.
6. **Surveiller sans rendre la main.** Répète, un appel à la fois, avec un délai d'outil de 600 000 ms :
   `sleep 540; tail -n 3 journal_K.log`.
   **Ne termine pas ton tour tant que la tranche tourne** : une session inactive est arrêtée et son
   calcul perdu. Dès qu'une course est finie, puis toutes les trois vérifications environ, sauvegarde
   sur ta branche de travail :
   `git add -f resultats/tranche_K.json journal_K.log && git commit -m "tranche K : partiel" && git push -u origin HEAD`
7. **Si le calcul s'est arrêté** (`pgrep -f "lancer.py --tranche"` ne renvoie rien) sans que le journal
   n'affiche `TRANCHE K TERMINÉE`, relance la commande de l'étape 5 : elle reprend là où elle s'était
   arrêtée, sans refaire les courses finies.
8. **À la fin** (`TRANCHE K TERMINÉE` dans le journal) : dernier commit et `git push -u origin HEAD`,
   puis réponds par les cinq dernières lignes du journal et le nom de ta branche. C'est terminé.

## Si le message dit « Rassemble »

1. `git fetch origin '+refs/heads/*:refs/remotes/origin/*'`
2. `python3 rassembler.py` — réunit, pour chaque tranche, les courses trouvées sur toutes les branches,
   dans `resultats/`, et écrit `resultats/bilan.txt`.
3. `git add -f resultats/` , commit, `git push -u origin HEAD`.
4. Réponds par le contenu de `resultats/bilan.txt` et le nom de ta branche.

## Ce que tu ne fais jamais

- Modifier un fichier suivi du dépôt (code, plan, pré-enregistrement, données, ces consignes) — même
  pour « corriger » ou « améliorer ». Seule exception : le rangement local de l'étape 0. Si quelque
  chose ne marche pas, arrête-toi et décris l'erreur.
- Analyser, résumer ou commenter les résultats : le verdict se fait ailleurs, selon la règle écrite
  avant les courses.
- Ouvrir une pull request, pousser sur `main` ou sur une autre branche que la tienne.
- Tout accès réseau autre que `pip install numpy` et `git` sur ce dépôt.
- Lancer une autre tranche que celle du message, ou plus d'une tranche à la fois.
