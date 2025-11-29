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

## Exemples

### Usage basique

Affiche les 20 derniers commits avec le graphe :

```bash
projects git-tree mon-projet
```

Résultat :
```
Git commit tree for 'mon-projet'

* fc9b7d3 - 4 hours ago style: enhance layout - Valentin (HEAD -> main)
* 8bbce4b - 5 hours ago refactor: rename battle - Valentin
* e7caf0a - 20 hours ago refactor: update imports - Valentin
* 5b92f74 - 20 hours ago refactor: reorganize - Valentin
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
Git commit tree for 'mon-projet' (all branches)

* a1b2c3d - 1 hour ago Feature X - Dev (feature/x)
| * d4e5f6g - 2 hours ago Fix bug - Dev (bugfix/auth)
|/
* h7i8j9k - 3 hours ago Merge branch - Main (HEAD -> main)
|\
| * k1l2m3n - 4 hours ago Add test - Dev
|/
* n4o5p6q - 5 hours ago Initial - Main
```

### Filtrer par auteur

```bash
projects git-tree mon-projet --author "Valentin"
```

### Combiner les options

```bash
projects git-tree mon-projet -n 100 --all --author "Valentin"
```

## Format de sortie

L'affichage utilise les couleurs natives de Git :
- **Jaune** : Hash du commit
- **Cyan** : Date relative
- **Blanc** : Message du commit
- **Gris** : Auteur
- **Coloré** : Références (branches, tags)

Les caractères `*`, `|`, `/`, `\` représentent le graphe des commits.

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

## Prérequis

- Le projet doit avoir un **path** configuré
- Le path doit pointer vers un **repo git**
- **Git** doit être installé et configuré

## Différence avec commits

| Commande | Format | Avantages |
|----------|--------|-----------|
| **commits** | Tableau formaté | ✅ Facile à lire<br>✅ Informations structurées<br>✅ Bon pour consultation rapide |
| **git-tree** | Graphe Git | ✅ Visualise les branches<br>✅ Montre les merges<br>✅ Format familier pour les utilisateurs Git |

Utilise **commits** pour une vue tabulaire claire, et **git-tree** pour comprendre la structure des branches.

## Exemples visuels

### Projet simple (une seule branche)

```bash
projects git-tree simple-projet -n 5
```

```
* f4148f7 - 2 hours ago I'm Batman - Valentin (HEAD -> main)
* 3a2b1c4 - 1 day ago Add feature - Valentin
* 5d6e7f8 - 2 days ago Fix bug - Valentin
* 9g8h7i6 - 3 days ago Update docs - Valentin
* 1j2k3l4 - 4 days ago Initial commit - Valentin
```

### Projet avec branches et merges

```bash
projects git-tree complex-projet --all -n 10
```

```
*   a1b2c3d - 1 hour ago Merge feature/auth - Main (HEAD -> main)
|\
| * d4e5f6g - 2 hours ago Add login form - Dev (feature/auth)
| * h7i8j9k - 3 hours ago Add auth service - Dev
|/
* k1l2m3n - 4 hours ago Update config - Main
*   n4o5p6q - 5 hours ago Merge bugfix - Main
|\
| * q7r8s9t - 6 hours ago Fix typo - Dev (bugfix/typo)
|/
* t1u2v3w - 7 hours ago Add tests - Main
```

## Voir aussi

- [commits](commits.md) - Historique en tableau
- [info](info.md) - Informations du projet
- [log](log.md) - Journal d'activité

---

**[← Retour aux commandes](../../COMMANDES.md)**
