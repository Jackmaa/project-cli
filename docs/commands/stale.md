# stale - Projets inactifs

Liste les projets sans activité depuis X jours.

## Synopsis

```bash
projects stale [OPTIONS]
```

## Options

| Option | Raccourci | Défaut | Description |
|--------|-----------|--------|-------------|
| `--days` | `-d` | 30 | Nombre de jours d'inactivité |

## Exemples

```bash
# Projets sans activité depuis 30 jours (défaut)
projects stale

# Projets sans activité depuis 60 jours
projects stale --days 60
# ou
projects stale -d 60

# Projets sans activité depuis 7 jours
projects stale -d 7
```

## Utilité

Identifie les projets que tu as peut-être oubliés ou abandonnés :

```bash
projects stale -d 90
```

Puis décide quoi en faire :
```bash
# Abandonner
projects status vieux-projet abandoned

# Ou supprimer
projects rm vieux-projet
```

## Voir aussi

- [status](status.md) - Changer le statut
- [rm](rm.md) - Supprimer un projet
- [stats](stats.md) - Statistiques globales

---

**[← Retour aux commandes](../../COMMANDES.md)**
