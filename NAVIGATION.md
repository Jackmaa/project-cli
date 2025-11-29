# 🧭 Navigation de la documentation

Ce fichier t'aide à naviguer dans toute la documentation du projet.

## 📁 Structure de la documentation

```
project-cli/
│
├── README.md              ← Point d'entrée principal
│
├── COMMANDES.md           ← Index de toutes les commandes
│
├── docs/
│   ├── README.md          ← Navigation et recherche
│   └── commands/          ← Documentation détaillée
│       ├── add.md
│       ├── list.md
│       ├── tag.md
│       ├── commits.md
│       ├── git-tree.md
│       ├── tree.md
│       ├── log.md
│       ├── github.md
│       ├── info.md
│       ├── edit.md
│       ├── rm.md
│       ├── status.md
│       ├── stats.md
│       ├── stale.md
│       └── scan.md
│
├── ARCHITECTURE.md        ← Architecture technique
│
└── CONTRIBUTING.md        ← Guide pour contribuer
```

## 🎯 Par où commencer ?

### Je suis un utilisateur

1. **Découverte** : Commence par le [README.md](README.md)
2. **Commandes** : Va voir [COMMANDES.md](COMMANDES.md) pour la liste complète
3. **Détails** : Clique sur une commande pour voir sa doc dans `docs/commands/`

### Je suis un développeur

1. **Comprendre** : Lis [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Contribuer** : Suis [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Exemples** : Regarde les fichiers dans `projects/commands/`

## 🔗 Liens rapides

### Documentation utilisateur

| Fichier | Description | Lien |
|---------|-------------|------|
| README.md | Vue d'ensemble et installation | [→ Voir](README.md) |
| COMMANDES.md | Index des commandes | [→ Voir](COMMANDES.md) |
| docs/README.md | Navigation et recherche | [→ Voir](docs/README.md) |

### Documentation développeur

| Fichier | Description | Lien |
|---------|-------------|------|
| ARCHITECTURE.md | Architecture modulaire | [→ Voir](ARCHITECTURE.md) |
| CONTRIBUTING.md | Ajouter une commande | [→ Voir](CONTRIBUTING.md) |

### Commandes (docs détaillées)

#### Gestion de base
- [add.md](docs/commands/add.md) - Ajouter un projet
- [list.md](docs/commands/list.md) - Lister les projets
- [info.md](docs/commands/info.md) - Détails d'un projet
- [edit.md](docs/commands/edit.md) - Modifier un projet
- [rm.md](docs/commands/rm.md) - Supprimer un projet
- [status.md](docs/commands/status.md) - Changer le statut

#### Organisation
- [tag.md](docs/commands/tag.md) - Gérer les tags
- [stats.md](docs/commands/stats.md) - Statistiques
- [stale.md](docs/commands/stale.md) - Projets inactifs

#### Import et visualisation
- [scan.md](docs/commands/scan.md) - Scanner des repos
- [tree.md](docs/commands/tree.md) - Arborescence des fichiers
- [commits.md](docs/commands/commits.md) - Historique Git (tableau)
- [git-tree.md](docs/commands/git-tree.md) - Historique Git (graphe)

#### Suivi et intégrations
- [log.md](docs/commands/log.md) - Journal d'activité
- [github.md](docs/commands/github.md) - Stats GitHub

## 🗺️ Parcours de lecture recommandés

### Parcours "Débutant"

1. [README.md](README.md) - Comprendre le projet
2. [COMMANDES.md](COMMANDES.md) - Voir toutes les commandes
3. [docs/commands/add.md](docs/commands/add.md) - Ajouter ton premier projet
4. [docs/commands/list.md](docs/commands/list.md) - Lister tes projets
5. [docs/commands/tag.md](docs/commands/tag.md) - Organiser avec des tags

### Parcours "Utilisateur avancé"

1. [docs/commands/scan.md](docs/commands/scan.md) - Importer tous tes repos
2. [docs/commands/log.md](docs/commands/log.md) - Journaliser ton activité
3. [docs/commands/git-tree.md](docs/commands/git-tree.md) - Visualiser l'historique
4. [docs/commands/github.md](docs/commands/github.md) - Suivre tes stats

### Parcours "Développeur"

1. [ARCHITECTURE.md](ARCHITECTURE.md) - Comprendre l'architecture
2. [CONTRIBUTING.md](CONTRIBUTING.md) - Apprendre à contribuer
3. Regarder le code dans `projects/commands/`
4. Créer ta première commande !

## 📖 Format des docs

Chaque documentation de commande suit ce format :

1. **Synopsis** - Comment utiliser la commande
2. **Arguments** - Arguments obligatoires
3. **Options** - Options facultatives
4. **Exemples** - Exemples d'utilisation
5. **Cas d'usage** - Scénarios réels
6. **Prérequis** - Ce dont tu as besoin
7. **Erreurs courantes** - Solutions aux problèmes
8. **Voir aussi** - Liens vers d'autres commandes

## 🆘 Besoin d'aide ?

### Aide en ligne de commande

```bash
# Aide générale
projects --help

# Aide sur une commande spécifique
projects add --help
projects list --help
```

### Documentation

- Consulte [COMMANDES.md](COMMANDES.md) pour trouver la commande
- Lis la doc détaillée dans `docs/commands/`
- Vérifie [docs/README.md](docs/README.md) pour la recherche

### Exemples

- Tous les fichiers de doc contiennent des exemples réels
- Le [README.md](README.md) contient des workflows complets
- [CONTRIBUTING.md](CONTRIBUTING.md) montre comment créer des commandes

---

Bonne lecture ! 📚
