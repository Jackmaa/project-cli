# commits - Historique Git (tableau)

Affiche l'historique des commits d'un projet dans un tableau formaté.

## Synopsis

```bash
projects commits <nom> [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Options

| Option | Raccourci | Type | Défaut | Description |
|--------|-----------|------|--------|-------------|
| `--limit` | `-n` | integer | 10 | Nombre de commits à afficher |
| `--author` | `-a` | string | - | Filtrer par auteur |

## Exemples

### Usage basique

Affiche les 10 derniers commits :

```bash
projects commits mon-projet
```

Résultat :
```
Commits for 'mon-projet'
╭─────────┬─────────────┬──────────┬─────────────────────────╮
│ Hash    │ Date        │ Author   │ Message                 │
├─────────┼─────────────┼──────────┼─────────────────────────┤
│ f4148f7 │ 2 hours ago │ Valentin │ Add new feature         │
│ 8bbce4b │ 5 hours ago │ Valentin │ Fix bug in login        │
│ e7caf0a │ 1 day ago   │ Valentin │ Update dependencies     │
╰─────────┴─────────────┴──────────┴─────────────────────────╯
```

### Limiter le nombre de commits

```bash
projects commits mon-projet --limit 20
# ou
projects commits mon-projet -n 20
```

### Filtrer par auteur

```bash
projects commits mon-projet --author "Valentin"
# ou
projects commits mon-projet -a "Valentin"
```

Fonctionne avec une partie du nom :
```bash
projects commits mon-projet --author "Val"
```

### Combiner les options

```bash
projects commits mon-projet -n 30 --author "Valentin"
```

## Informations affichées

Le tableau contient :
- **Hash** : Hash court du commit (7 caractères)
- **Date** : Date relative (ex: "2 hours ago", "3 days ago")
- **Author** : Nom de l'auteur
- **Message** : Message du commit

## Prérequis

- Le projet doit avoir un **path** configuré
- Le path doit pointer vers un **repo git** (contenant un dossier `.git`)
- **Git** doit être installé sur le système

## Erreurs courantes

### Projet non trouvé

```
✖ Project 'mon-projet' not found.
```

→ Vérifie le nom du projet avec `projects list`

### Pas de path configuré

```
✖ Project 'mon-projet' has no path set.
```

→ Ajoute un path avec `projects edit mon-projet --path /chemin/vers/projet`

### Pas un repo git

```
✖ 'mon-projet' is not a git repository.
```

→ Le dossier n'est pas un repo git. Initialise-le avec `git init` ou pointe vers le bon dossier.

### Git non installé

```
✖ Git is not installed or not in PATH.
```

→ Installe git : `sudo pacman -S git` (Arch) ou `sudo apt install git` (Ubuntu)

## Différence avec git-tree

| Commande | Format | Utilisation |
|----------|--------|-------------|
| **commits** | Tableau | Vue claire et lisible, bon pour une consultation rapide |
| **git-tree** | Graphe | Visualise les branches et merges, bon pour comprendre l'historique |

```bash
# Pour une vue rapide et claire
projects commits mon-projet -n 10

# Pour voir les branches et merges
projects git-tree mon-projet -n 20
```

## Voir aussi

- [git-tree](git-tree.md) - Historique en graphe
- [log](log.md) - Journaliser l'activité du projet
- [info](info.md) - Informations du projet

---

**[← Retour aux commandes](../../COMMANDES.md)**
