# edit - Modifier un projet

Modifie les informations d'un projet existant.

## Synopsis

```bash
projects edit <nom> [OPTIONS]
```

## Options

| Option | Description |
|--------|-------------|
| `--name` | Nouveau nom |
| `--desc`, `-d` | Nouvelle description |
| `--priority`, `-p` | Nouvelle priorité (high/medium/low) |

## Exemples

```bash
# Changer le nom
projects edit ancien-nom --name nouveau-nom

# Changer la description
projects edit mon-projet -d "Nouvelle description"

# Changer la priorité
projects edit mon-projet -p high

# Tout en même temps
projects edit mon-projet --name super-projet -d "Projet génial" -p high
```

## Voir aussi

- [add](add.md) - Ajouter un projet
- [info](info.md) - Voir les infos

---

**[← Retour aux commandes](../../COMMANDES.md)**
