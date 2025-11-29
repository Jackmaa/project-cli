# git-tree - Historique Git (graphe)

Affiche l'historique des commits sous forme de graphe (comme `git log --graph`).

## Synopsis

```bash
projects git-tree <nom> [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Options

| Option | Raccourci | Type | Défaut | Description |
|--------|-----------|------|--------|-------------|
| `--limit` | `-n` | integer | 20 | Nombre de commits à afficher |
| `--all` | `-a` | boolean | false | Afficher toutes les branches |
| `--author` | - | string | - | Filtrer par auteur |
| `--oneline` | `-o` | boolean | false | Format compact sur une ligne |
| `--stat` | `-s` | boolean | false | Afficher les statistiques de fichiers modifiés |

## Exemples

### Usage basique

Affiche les 20 derniers commits avec le graphe :

```bash
projects git-tree mon-projet
```

Résultat :
```
🌳 Git Tree: mon-projet
────────────────────────────────────────────────────────────────────────────────

* ◉ fc9b7d3  (HEAD -> main)
|   style: enhance layout
|   ✎ Valentin Gillot ✔ 4 hours ago (2025-11-29 08:30)
* ◉ 8bbce4b
|   refactor: rename battle
|   ✎ Valentin Gillot ✔ 5 hours ago (2025-11-29 07:30)
* ◉ e7caf0a
|   refactor: update imports
|   ✎ Valentin Gillot ✔ 20 hours ago (2025-11-28 16:30)
* ◉ 5b92f74
    refactor: reorganize
    ✎ Valentin Gillot ✔ 20 hours ago (2025-11-28 16:15)
```

### Afficher plus de commits

```bash
projects git-tree mon-projet --limit 50
# ou
projects git-tree mon-projet -n 50
```

### Afficher toutes les branches

Par défaut, seule la branche courante est affichée. Pour voir toutes les branches :

```bash
projects git-tree mon-projet --all
# ou
projects git-tree mon-projet -a
```

Résultat avec branches :
```
🌳 Git Tree: mon-projet (all branches)
────────────────────────────────────────────────────────────────────────────────

* ◉ a1b2c3d  (feature/x)
|   Feature X
|   ✎ Dev ✔ 1 hour ago (2025-11-29 11:30)
| * ◉ d4e5f6g  (bugfix/auth)
|/    Fix bug
|     ✎ Dev ✔ 2 hours ago (2025-11-29 10:30)
* ◉ h7i8j9k  (HEAD -> main)
|\    Merge branch
| |   ✎ Main ✔ 3 hours ago (2025-11-29 09:30)
| * ◉ k1l2m3n
|/    Add test
|     ✎ Dev ✔ 4 hours ago (2025-11-29 08:30)
* ◉ n4o5p6q
    Initial
    ✎ Main ✔ 5 hours ago (2025-11-29 07:30)
```

### Filtrer par auteur

```bash
projects git-tree mon-projet --author "Valentin"
```

### Mode compact (oneline)

Pour un affichage condensé sur une seule ligne par commit :

```bash
projects git-tree mon-projet --oneline
# ou
projects git-tree mon-projet -o
```

Résultat :
```
🌳 Git Tree: mon-projet (compact)
────────────────────────────────────────────────────────────────────────────────

* fc9b7d3 style: enhance layout (4 hours ago) (HEAD -> main)
* 8bbce4b refactor: rename battle (5 hours ago)
* e7caf0a refactor: update imports (20 hours ago)
* 5b92f74 refactor: reorganize (20 hours ago)
```

### Afficher les statistiques

Pour voir les fichiers modifiés dans chaque commit :

```bash
projects git-tree mon-projet --stat
# ou
projects git-tree mon-projet -s
```

### Combiner les options

```bash
projects git-tree mon-projet -n 100 --all --author "Valentin"
projects git-tree mon-projet --oneline --all -n 50
projects git-tree mon-projet --stat --limit 10
```

## Format de sortie

### Format détaillé (par défaut)

Chaque commit est affiché sur plusieurs lignes avec :
- **◉** : Symbole de commit avec hash en jaune
- **✎** : Icône d'auteur en bleu
- **✔** : Icône de date en vert
- Message du commit en blanc gras
- Date relative et absolue (`YYYY-MM-DD HH:MM`)
- Références colorées (branches, tags, HEAD)

### Format compact (`--oneline`)

Une seule ligne par commit avec :
- Hash court
- Message du commit en gras
- Date relative entre parenthèses
- Références colorées

### Graphe

Les caractères `*`, `|`, `/`, `\` représentent le graphe des commits et les branches.

## Cas d'usage

### Comprendre les branches

Avec `--all`, tu peux voir toutes les branches et leurs relations :

```bash
projects git-tree mon-projet --all
```

### Voir l'historique récent

Pour un coup d'œil rapide sur ce qui a été fait :

```bash
projects git-tree mon-projet -n 10
```

### Analyser les contributions

Pour voir ce qu'un contributeur a fait :

```bash
projects git-tree mon-projet --author "Alice" -n 50
```

### Vue rapide compacte

Pour parcourir rapidement beaucoup de commits :

```bash
projects git-tree mon-projet --oneline -n 100
```

### Analyser un commit en détail

Pour voir les fichiers modifiés dans chaque commit :

```bash
projects git-tree mon-projet --stat -n 5
```

## Prérequis

- Le projet doit avoir un **path** configuré
- Le path doit pointer vers un **repo git**
- **Git** doit être installé et configuré

## Différence avec commits

| Commande | Format | Avantages |
|----------|--------|-----------|
| **commits** | Tableau formaté | ✅ Facile à lire<br>✅ Informations structurées<br>✅ Bon pour consultation rapide |
| **git-tree** | Graphe Git détaillé | ✅ Visualise les branches<br>✅ Montre les merges<br>✅ Format enrichi avec emojis<br>✅ Mode compact disponible<br>✅ Statistiques optionnelles |

Utilise **commits** pour une vue tabulaire claire, et **git-tree** pour comprendre la structure des branches avec un affichage visuel amélioré.

## Exemples visuels

### Projet simple (une seule branche)

```bash
projects git-tree simple-projet -n 5
```

```
🌳 Git Tree: simple-projet
────────────────────────────────────────────────────────────────────────────────

* ◉ f4148f7  (HEAD -> main)
|   I'm Batman
|   ✎ Valentin ✔ 2 hours ago (2025-11-29 10:30)
* ◉ 3a2b1c4
|   Add feature
|   ✎ Valentin ✔ 1 day ago (2025-11-28 12:30)
* ◉ 5d6e7f8
|   Fix bug
|   ✎ Valentin ✔ 2 days ago (2025-11-27 14:15)
* ◉ 9g8h7i6
|   Update docs
|   ✎ Valentin ✔ 3 days ago (2025-11-26 09:45)
* ◉ 1j2k3l4
    Initial commit
    ✎ Valentin ✔ 4 days ago (2025-11-25 16:00)
```

### Projet avec branches et merges

```bash
projects git-tree complex-projet --all -n 10
```

```
🌳 Git Tree: complex-projet (all branches)
────────────────────────────────────────────────────────────────────────────────

*   ◉ a1b2c3d  (HEAD -> main)
|\    Merge feature/auth
| |   ✎ Main ✔ 1 hour ago (2025-11-29 11:30)
| * ◉ d4e5f6g  (feature/auth)
| |   Add login form
| |   ✎ Dev ✔ 2 hours ago (2025-11-29 10:30)
| * ◉ h7i8j9k
|/    Add auth service
|     ✎ Dev ✔ 3 hours ago (2025-11-29 09:30)
* ◉ k1l2m3n
|   Update config
|   ✎ Main ✔ 4 hours ago (2025-11-29 08:30)
*   ◉ n4o5p6q
|\    Merge bugfix
| |   ✎ Main ✔ 5 hours ago (2025-11-29 07:30)
| * ◉ q7r8s9t  (bugfix/typo)
|/    Fix typo
|     ✎ Dev ✔ 6 hours ago (2025-11-29 06:30)
* ◉ t1u2v3w
    Add tests
    ✎ Main ✔ 7 hours ago (2025-11-29 05:30)
```

## Voir aussi

- [commits](commits.md) - Historique en tableau
- [info](info.md) - Informations du projet
- [log](log.md) - Journal d'activité

---

**[← Retour aux commandes](../../COMMANDES.md)**
