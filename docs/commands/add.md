# add - Ajouter un projet

Ajoute un nouveau projet à la base de données.

## Synopsis

```bash
projects add <nom> [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Options

| Option | Raccourci | Type | Défaut | Description |
|--------|-----------|------|--------|-------------|
| `--desc` | `-d` | string | - | Description du projet |
| `--path` | `-p` | string | - | Chemin vers le projet |
| `--priority` | - | high/medium/low | medium | Priorité du projet |
| `--tags` | `-t` | string | - | Tags (séparés par des virgules) |

## Exemples

### Exemple basique

Ajouter un projet avec juste son nom :

```bash
projects add mon-projet
```

### Avec description

```bash
projects add mon-api --desc "API REST pour mon application"
```

### Avec path

Si tu fournis un path, le langage sera détecté automatiquement :

```bash
projects add mon-site --path ~/Work/mon-site
```

### Avec priorité

```bash
projects add projet-urgent --priority high
```

### Avec tags

```bash
projects add web-app --tags "web,react,typescript"
```

### Exemple complet

```bash
projects add super-projet \
  --desc "Mon super projet full-stack" \
  --path ~/Work/super-projet \
  --priority high \
  --tags "web,fullstack,react,node"
```

## Détection automatique

Quand tu fournis un `--path`, le CLI détecte automatiquement :

- **Le langage** : en analysant les extensions de fichiers
- **L'activité Git** : si c'est un repo git, récupère la date du dernier commit

Langages détectés :
- Python, JavaScript, TypeScript, Rust, Go, Java, C, C++, C#, Ruby, PHP, Swift, Kotlin, Dart, Vue, HTML, CSS, Shell

## Comportement

- ✅ Si le projet est ajouté avec succès, affiche un message de confirmation
- ❌ Si un projet avec le même nom existe déjà, affiche une erreur

## Voir aussi

- [edit](edit.md) - Modifier un projet existant
- [list](list.md) - Lister tous les projets
- [info](info.md) - Voir les détails d'un projet

---

**[← Retour aux commandes](../../COMMANDES.md)**
