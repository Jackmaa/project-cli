# status - Changer le statut

Change le statut d'un projet.

## Synopsis

```bash
projects status <nom> <nouveau-statut>
```

## Statuts disponibles

- `active` - Projet en cours
- `paused` - Projet en pause
- `completed` - Projet terminé
- `abandoned` - Projet abandonné

## Exemples

```bash
# Mettre en pause
projects status mon-projet paused

# Marquer comme terminé
projects status ancien-projet completed

# Abandonner
projects status vieux-projet abandoned

# Réactiver
projects status mon-projet active
```

## Voir aussi

- [list](list.md) - Filtrer par statut
- [stale](stale.md) - Projets inactifs

---

**[← Retour aux commandes](../../COMMANDES.md)**
