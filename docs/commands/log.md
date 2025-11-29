# log - Journaliser l'activité

Enregistre et affiche les logs d'activité sur tes projets.

## Synopsis

```bash
projects log [nom] [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (optionnel) |

## Options

| Option | Raccourci | Type | Défaut | Description |
|--------|-----------|------|--------|-------------|
| `--limit` | `-n` | integer | 20 | Nombre d'entrées à afficher |
| `--add` | `-a` | string | - | Ajouter une entrée de log |

## Exemples

### Ajouter une entrée

```bash
projects log mon-projet --add "Fixed authentication bug"
# ou
projects log mon-projet -a "Fixed authentication bug"
```

Résultat :
```
✔ Log entry added to 'mon-projet'.
```

### Voir les logs d'un projet

```bash
projects log mon-projet
```

Résultat :
```
Activity log for 'mon-projet'
╭───────────────────────┬──────────────────────────────────╮
│ Date                  │ Activity                         │
├───────────────────────┼──────────────────────────────────┤
│ 2025-11-29 10:58      │ Fixed authentication bug         │
│ (1h ago)              │                                  │
├───────────────────────┼──────────────────────────────────┤
│ 2025-11-28 14:30      │ Implemented user registration    │
│ (1d ago)              │                                  │
╰───────────────────────┴──────────────────────────────────╯
```

### Voir tous les logs (tous projets)

Sans spécifier de projet :

```bash
projects log
```

Résultat :
```
Recent activity (all projects)
╭──────────┬───────────────────────┬──────────────────────╮
│ Project  │ Date                  │ Activity             │
├──────────┼───────────────────────┼──────────────────────┤
│ web-app  │ 2025-11-29 10:58 (1h) │ Fixed auth bug       │
│ api      │ 2025-11-29 09:30 (2h) │ Added new endpoint   │
│ web-app  │ 2025-11-28 14:00 (1d) │ Updated dependencies │
╰──────────┴───────────────────────┴──────────────────────╯
```

### Limiter le nombre d'entrées

```bash
projects log mon-projet --limit 50
# ou
projects log -n 50
```

## Cas d'usage

### Journal de bord

Utilise `log` comme un journal de bord pour tracker ce que tu fais :

```bash
projects log mon-projet -a "Started working on the dashboard redesign"
projects log mon-projet -a "Implemented new chart component"
projects log mon-projet -a "Fixed responsive layout issues"
```

Plus tard :
```bash
projects log mon-projet
```

Tu retrouves tout ce que tu as fait ! 📝

### Suivre les jalons

```bash
projects log mon-projet -a "v1.0.0 released"
projects log mon-projet -a "Reached 1000 users milestone"
projects log mon-projet -a "MVP completed and deployed"
```

### Notes de debug

```bash
projects log api -a "Found memory leak in user service"
projects log api -a "Memory leak fixed - issue was in cache cleanup"
```

### Rappels et TODOs

```bash
projects log mon-projet -a "TODO: Optimize database queries"
projects log mon-projet -a "TODO: Add unit tests for auth module"
```

### Vue d'ensemble

Pour voir sur quoi tu as travaillé récemment :

```bash
projects log
```

Affiche les logs de **tous** les projets, triés par date.

## Stockage

Les logs sont stockés dans la table `activity_logs` de la base de données :
- Liés au projet
- Horodatés automatiquement
- Supprimés avec le projet (cascade)

## Conseils

💡 **Utilise un format cohérent** pour tes logs :

```bash
# Verbes d'action
projects log app -a "Added user authentication"
projects log app -a "Fixed navigation bug"
projects log app -a "Updated dependencies"

# Avec préfixes
projects log app -a "feat: Add dark mode"
projects log app -a "fix: Correct typo in footer"
projects log app -a "docs: Update README"
```

💡 **Logs vs Git commits** :

- **Git commits** : Changements de code
- **Logs** : Notes, jalons, réflexions, TODOs

Les deux sont complémentaires !

## Prérequis

Le projet doit exister dans la base de données.

## Voir aussi

- [commits](commits.md) - Historique Git
- [git-tree](git-tree.md) - Arbre des commits
- [info](info.md) - Informations du projet

---

**[← Retour aux commandes](../../COMMANDES.md)**
