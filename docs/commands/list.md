# list - Lister les projets

Affiche tous les projets dans un tableau formaté.

## Synopsis

```bash
projects list [OPTIONS]
```

## Options

| Option | Raccourci | Type | Description |
|--------|-----------|------|-------------|
| `--status` | `-s` | active/paused/completed/abandoned | Filtrer par statut |
| `--tag` | `-t` | string | Filtrer par tag |

## Exemples

### Lister tous les projets

```bash
projects list
```

Affiche :
```
Your Projects
╭────────────┬──────────┬──────────┬──────────┬──────────────┬──────╮
│ Name       │ Status   │ Priority │ Language │ Last Activity│ Tags │
├────────────┼──────────┼──────────┼──────────┼──────────────┼──────┤
│ web-app    │ ⚡ active│ 🔥 high   │ JS       │ 2h ago       │ web  │
│ old-proj   │ 🗑️ abandoned│ ○ low │ Python   │ 3mo ago      │ -    │
╰────────────┴──────────┴──────────┴──────────┴──────────────┴──────╯
```

### Filtrer par statut

Voir uniquement les projets actifs :

```bash
projects list --status active
# ou
projects list -s active
```

Statuts disponibles :
- `active` - Projets en cours
- `paused` - Projets en pause
- `completed` - Projets terminés
- `abandoned` - Projets abandonnés

### Filtrer par tag

Voir tous les projets web :

```bash
projects list --tag web
# ou
projects list -t web
```

### Combiner les filtres

```bash
projects list --status active --tag python
```

Affiche uniquement les projets **actifs** avec le tag **python**.

## Informations affichées

Le tableau affiche :
- **Name** : Nom du projet
- **Status** : Statut avec emoji (⚡ active, ⏸️ paused, ✔️ completed, 🗑️ abandoned)
- **Priority** : Priorité avec emoji (🔥 high, ● medium, ○ low)
- **Language** : Langage principal détecté
- **Last Activity** : Dernière activité Git (format relatif : "2h ago", "3d ago")
- **Tags** : Tags du projet

## Tri

Les projets sont triés par **date de mise à jour** (les plus récents en premier).

## Voir aussi

- [info](info.md) - Détails d'un projet spécifique
- [stats](stats.md) - Statistiques globales
- [stale](stale.md) - Projets inactifs

---

**[← Retour aux commandes](../../COMMANDES.md)**
