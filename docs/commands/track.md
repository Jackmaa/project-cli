# 📊 Commande `track`

Suivez le temps passé sur vos projets via des hooks git automatiques.

## 📋 Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Installation des hooks](#installation-des-hooks)
- [Utilisation](#utilisation)
- [Sous-commandes](#sous-commandes)
- [Exemples](#exemples)
- [Visualisations](#visualisations)

---

## Vue d'ensemble

La commande `track` vous permet de suivre automatiquement le temps passé sur vos commits. À chaque commit, un hook git vous demande combien de temps vous avez passé, puis enregistre cette information dans la base de données.

### Fonctionnalités

- ⏱️ **Suivi automatique** - Prompt après chaque commit
- 📊 **Visualisations** - Graphiques en terminal avec plotext
- 📈 **Agrégations** - Par jour ou par projet
- 🎯 **Multi-projets** - Installez les hooks sur tous vos projets
- 🔍 **Historique détaillé** - Consultez tous vos logs de commits

---

## Installation des hooks

Avant de pouvoir suivre le temps, vous devez installer les hooks git.

### Installation pour un projet

```bash
projects track install-hooks project-cli
```

### Installation pour tous les projets

```bash
projects track install-hooks --all
```

### Vérifier le statut

```bash
projects track status
```

Sortie :
```
                       Time Tracking Status
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Project            ┃ Git Repo ┃ Hooks Installed ┃ Status        ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ project-cli        │    ✓     │        ✓        │ Active        │
│ PokeBattleTower    │    ✓     │        ✗        │ Not installed │
└────────────────────┴──────────┴─────────────────┴───────────────┘
```

---

## Utilisation

### Workflow typique

1. **Installez le hook** sur votre projet
2. **Travaillez normalement** sur votre code
3. **Commitez** vos changements
4. **Répondez au prompt** pour indiquer le temps passé (ou appuyez sur Entrée pour ignorer)
5. **Consultez vos statistiques** avec les commandes de visualisation

### Exemple de prompt après commit

```bash
git commit -m "feat: Add new feature"

============================================================
Time Tracking - How long did this commit take?
============================================================
Enter time in minutes (or press Enter to skip): 45
✓ Logged 45 minutes for this commit
============================================================

[main abc1234] feat: Add new feature
 3 files changed, 150 insertions(+), 20 deletions(-)
```

---

## Sous-commandes

### `install-hooks`

Installe le hook post-commit pour le suivi du temps.

```bash
# Un projet
projects track install-hooks <nom-projet>

# Tous les projets
projects track install-hooks --all
```

**Options:**
- `--all` : Installer sur tous les projets

### `uninstall-hooks`

Désinstalle le hook post-commit.

```bash
# Un projet
projects track uninstall-hooks <nom-projet>

# Tous les projets
projects track uninstall-hooks --all
```

**Options:**
- `--all` : Désinstaller de tous les projets

### `status`

Affiche le statut d'installation des hooks pour tous les projets.

```bash
projects track status
```

### `log`

Affiche l'historique détaillé des commits avec le temps enregistré.

```bash
# Tous les projets (30 derniers jours)
projects track log

# Un projet spécifique
projects track log project-cli

# Période personnalisée
projects track log project-cli --days 7
```

**Options:**
- `--days N` / `-d N` : Nombre de jours à afficher (défaut: 30)

**Sortie:**
```
                  Commit Time Logs (Last 30 days)
┏━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━┓
┃ Date       ┃ Project     ┃ Commit  ┃ Message           ┃ Time ┃ Branch ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━┩
│ 2025-12-05 │ project-cli │ d32ba7b │ feat: Add time... │  45m │ main   │
│ 2025-12-05 │ project-cli │ abc1234 │ fix: Bug fix      │  20m │ main   │
└────────────┴─────────────┴─────────┴───────────────────┴──────┴────────┘

Total: 2 commits, 1h 5m
```

### `summary`

Affiche un résumé agrégé du temps passé.

```bash
# Par jour (défaut)
projects track summary

# Par projet
projects track summary --by-project

# Avec graphique
projects track summary --chart

# Période personnalisée
projects track summary --days 7 --chart
```

**Options:**
- `--days N` / `-d N` : Nombre de jours (défaut: 30)
- `--by-project` : Grouper par projet au lieu de par jour
- `--chart` : Afficher un graphique (nécessite plotext)

**Sortie par jour:**
```
Time Summary by Day (Last 30 days)
┏━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Day        ┃ Commits ┃ Total Time ┃
┡━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2025-12-05 │       8 │      3h 20m│
│ 2025-12-04 │      12 │      5h 45m│
│ 2025-12-03 │       5 │      2h 10m│
└────────────┴─────────┴────────────┘

Total: 25 commits, 11h 15m
```

**Sortie par projet:**
```
Time Summary by Project (Last 30 days)
┏━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Project     ┃ Commits ┃ Total Time ┃
┡━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━┩
│ project-cli │      15 │      8h 30m│
│ my-website  │      10 │      2h 45m│
└─────────────┴─────────┴────────────┘

Total: 25 commits, 11h 15m
```

---

## Visualisations

### Graphique terminal avec `--chart`

Utilisez l'option `--chart` pour afficher un graphique en barres directement dans le terminal :

```bash
projects track summary --chart
```

**Résultat:**
```
Time Spent (minutes per day)
300 ┤     ╭─╮
250 ┤     │ │  ╭─╮
200 ┤  ╭─╮│ │  │ │
150 ┤  │ ││ │╭─╯ │
100 ┤╭─╯ ││ ││   │
 50 ┤│   ││ ││   │
  0 ┴┴───┴┴─┴┴───┴
    Mon Tue Wed Thu Fri
Minutes                 Date
```

---

## Exemples

### Scénario 1: Démarrage sur un nouveau projet

```bash
# 1. Installer le hook
projects track install-hooks my-project

# 2. Travailler et commiter normalement
git commit -m "feat: Initial setup"
# Prompt: Enter time in minutes: 30

# 3. Consulter vos stats
projects track log my-project
```

### Scénario 2: Revue hebdomadaire

```bash
# Voir le temps total par projet cette semaine
projects track summary --by-project --days 7

# Avec graphique
projects track summary --days 7 --chart
```

### Scénario 3: Installation massive

```bash
# Installer sur tous vos projets git
projects track install-hooks --all

# Vérifier l'installation
projects track status
```

### Scénario 4: Analyse de productivité

```bash
# Voir l'évolution sur le mois
projects track summary --days 30 --chart

# Détail des commits
projects track log --days 30
```

---

## Détails techniques

### Stockage

Le temps est enregistré dans la table `commit_time_logs` de la base de données SQLite (`~/.config/project-cli/projects.db`).

### Hook post-commit

Le hook est installé dans `.git/hooks/post-commit` de chaque projet. Il :
1. Récupère les infos du commit (hash, message, auteur, date, branche)
2. Demande le temps passé via `/dev/tty` (pour fonctionner même avec stdin redirigé)
3. Enregistre les données dans la base de données
4. Gère gracieusement les erreurs (EOFError, KeyboardInterrupt)

### Sécurité

- Les hooks contiennent un marqueur `# DO NOT EDIT - Managed by project-cli`
- La désinstallation vérifie ce marqueur avant de supprimer
- Pas de suppression de hooks personnalisés

---

## Conseils

### 💡 Bonnes pratiques

1. **Soyez honnête** - Entrez le temps réel passé, pas le temps "idéal"
2. **Commitez souvent** - Des commits plus petits = meilleur suivi
3. **Utilisez Enter pour ignorer** - Pas besoin de tout tracker, seulement les commits significatifs
4. **Consultez régulièrement** - Utilisez `--chart` pour visualiser vos tendances

### ⚠️ Limitations

- Le temps est enregistré **par commit**, pas en temps réel
- Nécessite une interaction manuelle après chaque commit
- Fonctionne uniquement avec les repos git
- Les hooks doivent être réinstallés si le dossier `.git` est supprimé

### 🔧 Dépannage

**Le hook ne prompt pas:**
- Vérifiez que le hook est installé : `projects track status`
- Réinstallez si nécessaire : `projects track install-hooks <projet>`

**Le graphique ne s'affiche pas:**
- Vérifiez que plotext est installé : `pip list | grep plotext`
- Installez si nécessaire : `pip install plotext`

**Les dates sont incorrectes:**
- Le fuseau horaire est géré automatiquement par git
- Les dates sont enregistrées au format ISO 8601

---

## Voir aussi

- [log](log.md) - Journalisation générale d'activité
- [stats](stats.md) - Statistiques globales des projets
- [commits](commits.md) - Historique git détaillé

---

**[← Retour aux commandes](../../COMMANDES.md)** | **[README →](../../README.md)**
