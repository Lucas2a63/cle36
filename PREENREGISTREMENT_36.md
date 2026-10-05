# Clé 36 — À l'échelle : prédictions pré-enregistrées

Écrit le 24 septembre 2026 à 11 h 51 (Paris), **avant toute course de la clé 36**.

Ce qui a tourné avant, et rien d'autre :
1. le contrôle des gradients des deux réseaux par différences finies (`controle_gradients.py`) ;
2. des réseaux **isolés** — sans sélection, sans curation, sans poids de classe, quatre taux
   d'apprentissage fixes, graine 99 hors plan — pour vérifier que les données chargent et que chaque
   architecture apprend. Précision dans le monde après 120 générations : perceptron 0,40 à 0,45,
   réseau convolutif 0,53 à 0,58. Deux versions du réseau convolutif y ont été comparées (moyenne
   2×2 après la première convolution, ou première convolution de pas 2) : 1 à 3 points d'écart en
   faveur de la première, la seconde 1,5 à 1,7 fois plus rapide ; la seconde est retenue ;
3. sur ces mêmes réseaux isolés, la **décision pondérée** argmax_k w_k p_k(x), le chat pesé ×c
   (tableau plus bas) — ce vers quoi pousse une perte pondérée ×c, à représentation égale ;
4. chaque chemin du code pendant 2 à 36 générations (graine 99) pour la structure des sorties et le
   chronométrage, sans lecture des mesures.

## La question

Les clés 33 à 35 ont été faites sur MNIST et Fashion-MNIST, avec 16 perceptrons de 32 neurones.
Elles ont établi, entre autres : qu'une population classée sur sa propre réussite ment et élague le
rare vital ; qu'une validation figée trompe quand le monde bouge ; que seule l'ancre fraîche, visée
sur la classe fatale et pondérée par le coût, apprend ce qui compte et donne la meilleure vérité
(clé 33) ; que peser trop n'est presque gratuit que par un canal lent et sur une classe séparable ;
que, mis directement dans la perte, le poids vrai est le meilleur ; qu'un poids fort imposé d'emblée
fait geler le système au démarrage ; que la représentation s'use sans s'effondrer (clé 35).

La clé 36 rejoue le cœur de ces deux clés **sur des images naturelles**, avec une population deux
fois plus grande, des réseaux quatre fois plus larges, un **réseau convolutif** (des filtres partagés
par toutes les classes : les « couches partagées » de l'objection de Lucas à la clé 35), un troisième
monde qui **se dégrade**, et un **banc de stress** final — les deux dernières choses reprises du
tableau de Lucas (ImageNet-C, ObjectNet), à l'échelle de ce bac à sable.

## Le montage

- **Données** : CIFAR-10 (Krizhevsky, 2009), archive originale (MD5 vérifié), réduite en 16×16
  couleur par moyenne des blocs 2×2, centrée-réduite par canal. Des 50 000 images d'entraînement,
  35 000 forment le flux du monde et 15 000 la réserve où l'on tire les tests (découpage fixe).
  Les 10 000 images de test sont **le juge**, que ni la population ni la sélection ne voient jamais.
  Quand une classe est épuisée dans la réserve, elle est recyclée (comme depuis la clé 34) : sous
  ANCRÉ, les 1 508 chats de la réserve sont revus environ toutes les 38 générations ; sous FRAIS et
  ANCRÉ, les classes ordinaires le sont une fois, après la génération 70 à 85.
- **La classe fatale est le chat** (étiquette 3) : 3 % du monde, coût ×30 pour le juge (48 % de la
  masse de coût). C'est la classe la plus emmêlée du jeu.
- **Population** : 32 réseaux. Génome héréditaire : taux d'apprentissage, régularisation, vitesse de
  curation ε, un poids par classe dans la perte (bornes [×0,01 ; ×100]). Tampon de 5 000 images, 500
  arrivées par génération, 100 pas de gradient de 64 images, 120 générations. À chaque génération, les
  8 derniers sont remplacés par des copies mutées des 8 premiers (mutations des clés 33 à 35).
- **Architectures** : perceptron 768 → 128 → 10 (tanh) ; réseau convolutif : convolution 3×3 de pas 2
  (16 filtres) → convolution 3×3 (32 filtres) → moyenne 2×2 → 512 → 10 (tanh).
- **Régimes** (sur quoi la population est classée) : AUTO (sa propre réussite sur 200 images tirées
  par sa curation), FIGÉ (1 000 images tirées une fois, au départ, réutilisées), FRAIS (200 images
  neuves), ANCRÉ (200 images neuves dont 40 chats, repondérées sans biais, chat pesé ×c).
- **Mondes** : fixe ; qui tourne (0° → 45°) ; qui se dégrade (sévérité 0 → 1 ; chaque image reçoit une
  corruption parmi quatre : bruit gaussien d'écart-type 0,10·s, flou gaussien de 1,0·s pixel, contraste
  ×(1 − 0,8·s), pixellisation de 16 à 16 − 8·s ; à s = 1, à peu près la sévérité 5 de CIFAR-10-C).
- **Valeur** (comment le poids du chat atteint le réseau) : SEL (héréditaire, choisi par la seule
  sélection), IMP (×c imposé dans la perte dès le départ), DIF (×1 jusqu'à la génération 30, puis ×c
  d'un coup), RAM (de ×1 à ×c en montée géométrique jusqu'à la génération 30, puis ×c). Dans tous les
  cas, l'ancre classe la population avec le chat pesé ×c.
- **Le juge** : les 10 000 images de test dans l'état courant du monde (tirages fixés, les mêmes pour
  toutes les courses), aux générations 0, 1, 2, 4, 8, 16, 24, 29, 31, 32, 33, 35, 39, 40, 48, 56, 59,
  64, 72, 80, 88, 96, 104, 112, 119.
- **Mesures finales** (génération 119, images propres) : sonde linéaire (moindres carrés régularisés,
  λ = 1, sur les traits de l'avant-dernière couche — 128 neurones du perceptron, 512 traits du réseau
  convolutif — apprise sur 500 images de la réserve par classe ordinaire) ; front de réglage (biais
  ajouté au seul logit du chat) ; dimension effective (rapport de participation des traits).
- **Banc de stress final** : 2 000 images de test (200 par classe), sous 15 perturbations — chacune
  des quatre corruptions aux sévérités 1/3, 2/3 et 1, et des rotations de 15°, 30° et 45°.

## Le plan : 396 courses, graines 0 à 11

- **I** — perceptron, poids héréditaire, ancre ×30 : 4 régimes × 3 mondes (144 courses).
- **II** — perceptron, régime ancré, monde fixe : IMP ×1, ×3, ×10, ×30, ×100, ×300, ×1000 ; SEL ×1 et
  ×1000 (SEL ×30 est la course ANCRÉ-fixe de I) ; DIF ×30 et ×1000 ; RAM ×1000 (144 courses).
- **III** — réseau convolutif, monde fixe : ANCRÉ avec IMP ×1, ×30, ×1000, SEL ×1, ×30, ×1000, DIF
  ×1000 ; AUTO et FRAIS (108 courses).

## Définitions

- **Vérité** (V30) : rappel par classe pondéré par la masse de coût du monde (chat ×30), lu par le juge.
  Partie A : celle du **meilleur** réseau de la génération (comme la clé 33). Parties B et C : moyenne
  de la **population** (comme la clé 35).
- **Mensonge** : note affichée du meilleur réseau (son score de sélection) moins la même grandeur lue
  par le juge sur ce réseau — précision simple (pondérée par le monde) sous AUTO, FIGÉ et FRAIS, vérité
  ×30 sous ANCRÉ. **Mensonge de population** : note moyenne moins la même grandeur moyenne du juge.
- **R_chat** : rappel du chat. **A_ord** : moyenne des rappels des neuf classes ordinaires.
  **FA** : part des images ordinaires prises pour des chats. Un réseau est **gelé** si FA > 0,5 ; la
  **fraction gelée** est la part des 32 réseaux gelés.
- **Poids interne** : poids du chat dans la perte rapporté à la moyenne des autres (moyenne des logs).
- **Fin de course** : génération 119. Écarts **appariés** graine par graine.

## Ce que le pilote a montré (et qui a informé les prédictions B3b et B5)

Décision pondérée appliquée aux sorties des réseaux isolés (entraînés à ×1), chat pesé ×c :

| ×c | perceptron : FA | perceptron : V30 | convolutif : FA | convolutif : V30 |
|---|---|---|---|---|
| ×1 | 0,01 | 0,24–0,26 | 0,00–0,01 | 0,32–0,35 |
| ×30 | 0,24–0,41 | 0,42–0,54 | 0,17–0,39 | 0,51–0,65 |
| ×100 | 0,40–0,64 | 0,49–0,56 | 0,29–0,58 | 0,57–0,64 |
| ×1000 | 0,69–0,90 | 0,52–0,55 | 0,53–0,82 | 0,55–0,61 |

Deux choses en sortent. À ×1000, même des réseaux bien entraînés prennent la majorité des images
ordinaires pour des chats : sur CIFAR, **le gel est l'optimum d'une perte pesée ×1000**, pas seulement
un accident de démarrage. Et le perceptron **sous-estime** le chat : la décision qui maximise la vérité
du juge est au-dessus du coût vrai (×100 à ×1000 selon le réseau), alors que pour le réseau
convolutif, meilleur, elle revient à ×30–×100 (sauf pour le moins bien entraîné des quatre).

## Les prédictions

### A — Le cœur de la clé 33 à l'échelle (perceptron ; dans chacun des trois mondes)

- **A1 — La boucle fermée ment le plus.** Mensonge final AUTO > FIGÉ, > FRAIS, > ANCRÉ ; et mensonge
  AUTO > 0,10 (moyenne des graines) — dans les trois mondes, là où la clé 33 ne l'avait vu que dans le
  monde qui tourne.
- **A2 — La validation figée.** Monde fixe : mensonge FIGÉ > 0. Mondes qui bougent (tourne, se
  dégrade) : vérité FRAIS > vérité FIGÉ.
- **A3 — Nouveau : la malédiction du vainqueur.** À l'échelle, la prédiction P3 de la clé 33 (l'ancre
  fraîche ne ment pas : |mensonge| < 0,03) **échoue pour le meilleur réseau** et **tient pour la
  population** :
  - **A3a** : sous FRAIS et sous ANCRÉ, le mensonge final du meilleur dépasse 0,03 (moyenne des graines)
    et est positif (t > 2). Le meilleur de 32 réseaux, choisi sur 200 images (40 chats), l'est en
    partie pour sa chance : avec une précision de 0,45 au lieu de 0,9, et deux fois plus de candidats,
    l'optimisme du vainqueur dépasse la marge qui tenait sur MNIST ;
  - **A3b** : sous FRAIS et sous ANCRÉ, le mensonge de population reste sous 0,03 en valeur absolue
    (moyenne des graines) à chaque passage du juge.
- **A4 — Le rare vital** (rappel du chat, meilleur réseau) : AUTO < FIGÉ, AUTO < FRAIS ; ANCRÉ > AUTO,
  > FIGÉ, > FRAIS. (Ma confiance est haute pour ANCRÉ, faible pour AUTO contre FIGÉ et FRAIS, où les
  trois régimes non ancrés oublient presque tous le chat.)
- **A5 — Seul l'ancré apprend ce qui compte.** Poids interne du chat sous ANCRÉ > 1, et > celui de
  chacun des trois autres régimes.
- **A6 — Le rang contre l'abri** (mondes qui bougent) : ε final AUTO > FRAIS, AUTO > ANCRÉ.
- **A7 — Monde fixe** : ε descend sous FRAIS et sous ANCRÉ (ε à la génération 0 > ε final).
- **A8 — L'architecture.** Vérité finale ANCRÉ > AUTO, > FIGÉ, > FRAIS.
- **A9 — Les tests de stress.** Sur le banc de stress final, la vérité moyenne de la population sur
  les 15 perturbations est plus haute sous ANCRÉ que sous chacun des trois autres régimes.

### B — Le cœur de la clé 35 à l'échelle (perceptron ; monde fixe ; régime ancré)

- **B1 — Sous gradient direct, l'excès se paie.** IMP : A_ord(×1000) − A_ord(×30) ≤ −3 points (t > 2).
  Démenti si l'écart dépasse −1 point.
- **B1b — Le gel sur classe emmêlée** (Lucas, confirmé à la clé 35 sur Fashion ; je m'y range) :
  IMP : A_ord(×300) − A_ord(×30) ≤ −10 points (t > 2). Démenti si l'écart dépasse −3 points.
- **B2 — Le cliquet protège.** La perte d'A_ord de ×30 à ×1000 est plus grande sous IMP que sous SEL
  (différence des différences < 0, t > 2).
- **B3 — Peser le chat compte.** IMP : V30(×30) > V30(×1).
- **B3b — Peser plus que juste.** IMP : le meilleur point de la grille (V30, moyenne des graines) est
  **au-dessus** de ×30 (×100, ×300 ou ×1000). À la clé 35, c'était ×30. Raison : le pilote montre que
  le perceptron sous-estime le chat sur CIFAR ; le poids qui sert le mieux le juge compense cette
  sous-estimation.
- **B4 — Le gel de démarrage.** IMP ×1000 : fraction gelée ≥ 0,5 à la génération 0. SEL ×1000 :
  fraction gelée ≤ 0,05 aux générations 0, 1, 2, 4 et 8.
- **B5 — Canal ou démarrage : la question que la clé 35 laissait ouverte.** Je prédis **le canal** :
  sur CIFAR, un poids de ×1000 fait geler aussi un système déjà entraîné, parce que le gel est
  l'optimum de la perte qu'il définit.
  - DIF ×1000 : fraction gelée ≥ 0,5 à la génération 35 (cinq générations après la bascule) ;
  - RAM ×1000 : fraction gelée ≥ 0,5 à la génération 35 ;
  - en fin de course, |A_ord(DIF ×1000) − A_ord(IMP ×1000)| < 3 points : le démarrage ne laisse pas de
    trace durable (démenti si l'écart atteint 3 points avec t > 2) ;
  - de même au poids vrai : |V30(DIF ×30) − V30(IMP ×30)| < 2 points en fin de course.
- **B6 — La représentation s'use** (Lucas, clé 35 T4a, alors démenti à −2,5 points ; **je change
  d'avis pour CIFAR**) : sonde(×1000) − sonde(×30), IMP, ≤ −5 points (t > 2). Raison : sur des images
  naturelles, des traits aléatoires valent peu ; ce que le poids ×1000 affame — le gradient des classes
  ordinaires — est ce qui construit la représentation.
- **B7 — Une névrose de représentation, pas seulement de seuil** : IMP ×1000 fait moins bien que la
  population ×30 de la même graine rereglée par son seul seuil jusqu'au même rappel du chat ; écart
  ≤ −2 points (t > 2).
- **B8 — Les représentations s'alignent sur le danger** (Lucas, clé 35 T4d) : dimension effective
  IMP ×1000 < IMP ×30 (t > 2).

### C — Les deux cœurs sur un réseau convolutif (monde fixe)

- **C1** = B1 ; **C2** = B2 ; **C3** : IMP V30(×30) > V30(×1) **et** V30(×30) > V30(×1000) (le
  réseau convolutif, mieux calibré, revient au poids vrai — confiance moyenne : au pilote, deux des
  quatre réseaux décidaient au moins aussi bien à ×1000 qu'à ×30) ; **C4** = B4 ; **C5** : DIF ×1000 fraction
  gelée ≥ 0,5 à la génération 35, et |A_ord(DIF ×1000) − A_ord(IMP ×1000)| < 3 points en fin de
  course ; **C6** = B6 ; **C7** = B7 ; **C8** = B8. Ma confiance est plus faible pour C5 : au pilote,
  l'un des quatre réseaux convolutifs ne franchissait le seuil de gel qu'à peine à ×1000 (FA 0,53).
- **C9 — La clé 33 sur le réseau convolutif** : mensonge AUTO > FRAIS, > ANCRÉ, et > 0,10 ; A3a et A3b
  pour FRAIS et ANCRÉ ; rappel du chat et vérité : ANCRÉ > AUTO, > FRAIS.

## Règle de décision

Comme aux clés 33 à 35. Comparaisons appariées graine par graine ; **confirmé** si l'écart a le signe
prédit avec t > 2 ; **démenti** s'il est significatif dans l'autre sens ; **indécidable** sinon. Les
seuils chiffrés sont jugés sur la moyenne des graines, avec les bornes de démenti écrites ci-dessus.
Une prédiction « sans écart durable » (B5, C5) est confirmée si l'écart moyen est sous la borne,
démentie s'il la dépasse avec t > 2. Une prédiction démentie reste démentie telle qu'enregistrée.
`verdict36.py`, haché avec ce fichier, applique cette règle telle qu'écrite.

Si des courses manquent (session perdue), le verdict porte sur les graines complètes pour chaque
comparaison, et le nombre de graines est rapporté.

## Ce qui sera rapporté sans être testé

Les courbes au fil des générations ; la vérité par perturbation du banc de stress ; la comparaison
des deux architectures (usure de la sonde, gel, vitesse) ; la dispersion entre graines (l'« équilibre
instable » de Lucas) ; le coût réel de la campagne en temps et en crédits.
