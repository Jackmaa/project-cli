# stats - Statistiques

Affiche des statistiques sur tous les projets.

## Synopsis

```bash
projects stats
```

## Exemple

```bash
projects stats
```

Résultat :
```
Project Statistics
╭────────────────────────┬───────╮
│ Metric                 │ Value │
├────────────────────────┼───────┤
│ Total Projects         │ 15    │
│                        │       │
│ ⚡ Active              │ 8     │
│ ⏸️ Paused              │ 3     │
│ ✔️ Completed           │ 2     │
│ 🗑️ Abandoned           │ 2     │
│                        │       │
│ 🔥 High                │ 5     │
│ ● Medium               │ 8     │
│ ○ Low                  │ 2     │
│                        │       │
│ Oldest Stale Project   │ old-project (3mo ago) │
╰────────────────────────┴───────╯
```

## Informations affichées

- Total de projets
- Répartition par statut
- Répartition par priorité
- Projet le plus ancien sans activité

## Voir aussi

- [list](list.md) - Lister les projets
- [stale](stale.md) - Projets inactifs

---

**[← Retour aux commandes](../../COMMANDES.md)**
