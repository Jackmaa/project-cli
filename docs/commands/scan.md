# scan - Scanner des repositories

Scanne un dossier pour trouver tous les repos git et les importer automatiquement.

## Synopsis

```bash
projects scan <dossier> [OPTIONS]
```

## Options

| Option | Raccourci | Description |
|--------|-----------|-------------|
| `--depth` | `-d` | Profondeur maximum de scan |
| `--dry-run` | - | Simuler sans importer |

## Exemples

```bash
# Scanner ton dossier de travail
projects scan ~/Work

# Limiter la profondeur à 2 niveaux
projects scan ~/Work --depth 2

# Voir ce qui serait importé (sans importer)
projects scan ~/Work --dry-run
```

## Fonctionnement

1. Scanne le dossier récursivement
2. Trouve tous les dossiers contenant `.git`
3. Pour chaque repo :
   - Détecte le langage
   - Récupère la dernière activité git
   - Importe le projet
4. Skip les projets déjà existants

## Exemple de sortie

```bash
projects scan ~/Work
```

```
ℹ Scanning /home/user/Work for git repositories...
ℹ Found 5 git repositories.
✔ Imported: web-app
✔ Imported: api-backend
✔ Imported: cli-tool
  Skipped: existing-project (already exists)
✔ Imported: game-project

Imported 4 projects, skipped 1.
```

## Cas d'usage

### Import initial

Première utilisation du CLI :
```bash
projects scan ~/Work
```

Importe tous tes projets d'un coup !

### Vérifier les nouveaux projets

Périodiquement :
```bash
projects scan ~/Work --dry-run
```

Voir si tu as créé de nouveaux projets.

## Voir aussi

- [add](add.md) - Ajouter un projet manuellement
- [list](list.md) - Voir les projets importés

---

**[← Retour aux commandes](../../COMMANDES.md)**
