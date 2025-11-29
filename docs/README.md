# Documentation du projet

Bienvenue dans la documentation du CLI `projects` !

## 📚 Navigation

### Pour les utilisateurs

- **[COMMANDES.md](../COMMANDES.md)** - Liste complète des commandes avec liens vers la doc détaillée
- **[docs/commands/](commands/)** - Documentation détaillée de chaque commande

### Pour les développeurs

- **[ARCHITECTURE.md](../ARCHITECTURE.md)** - Comprendre l'architecture modulaire
- **[CONTRIBUTING.md](../CONTRIBUTING.md)** - Ajouter une nouvelle commande

## 🎯 Commandes par catégorie

### Gestion de base
- [add](commands/add.md) - Ajouter un projet
- [list](commands/list.md) - Lister les projets
- [info](commands/info.md) - Détails d'un projet
- [edit](commands/edit.md) - Modifier un projet
- [rm](commands/rm.md) - Supprimer un projet
- [status](commands/status.md) - Changer le statut

### Organisation
- [tag](commands/tag.md) - Gérer les tags
- [stats](commands/stats.md) - Statistiques
- [stale](commands/stale.md) - Projets inactifs

### Import
- [scan](commands/scan.md) - Scanner des repos

### Visualisation
- [tree](commands/tree.md) - Arborescence des fichiers
- [commits](commands/commits.md) - Historique Git (tableau)
- [git-tree](commands/git-tree.md) - Historique Git (graphe)

### Suivi
- [log](commands/log.md) - Journal d'activité

### Intégrations
- [github](commands/github.md) - Stats GitHub

## 🔍 Recherche rapide

### Je veux...

- **Ajouter un projet** → [add](commands/add.md)
- **Voir tous mes projets** → [list](commands/list.md)
- **Trouver les projets Python** → [list](commands/list.md) (avec `--tag python`)
- **Voir l'historique Git** → [commits](commands/commits.md) ou [git-tree](commands/git-tree.md)
- **Explorer un projet** → [tree](commands/tree.md)
- **Noter ce que j'ai fait** → [log](commands/log.md)
- **Voir les stats GitHub** → [github](commands/github.md)
- **Trouver les projets abandonnés** → [stale](commands/stale.md)
- **Importer mes repos** → [scan](commands/scan.md)

## 🚀 Aide

Pour l'aide intégrée dans le terminal :

```bash
# Aide générale
projects --help

# Aide sur une commande
projects <commande> --help
```

---

**[← Retour au README](../README.md)**
