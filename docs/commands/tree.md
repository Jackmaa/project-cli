# tree - Arborescence des fichiers

Affiche la structure des fichiers et dossiers d'un projet sous forme d'arbre.

## Synopsis

```bash
projects tree <nom> [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Options

| Option | Raccourci | Type | Défaut | Description |
|--------|-----------|------|--------|-------------|
| `--depth` | `-d` | integer | ∞ | Profondeur maximum de l'arbre |
| `--all` | `-a` | boolean | false | Afficher les fichiers cachés (commençant par .) |

## Exemples

### Usage basique

Affiche toute l'arborescence :

```bash
projects tree mon-projet
```

Résultat :
```
📦 mon-projet
├── 📁 src
│   ├── 🐍 main.py
│   ├── 🐍 utils.py
│   └── 📁 models
│       ├── 🐍 user.py
│       └── 🐍 project.py
├── 📝 README.md
├── ⚙️ pyproject.toml
└── 🔧 setup.sh
```

### Limiter la profondeur

Pour ne pas être submergé dans les gros projets :

```bash
projects tree mon-projet --depth 2
# ou
projects tree mon-projet -d 2
```

Résultat :
```
📦 mon-projet
├── 📁 src
│   ├── 🐍 main.py
│   ├── 🐍 utils.py
│   └── 📁 models
├── 📝 README.md
└── ⚙️ pyproject.toml
```

### Afficher les fichiers cachés

Par défaut, les fichiers commençant par `.` sont masqués :

```bash
projects tree mon-projet --all
# ou
projects tree mon-projet -a
```

Affichera aussi `.git`, `.gitignore`, `.env`, etc.

### Combiner les options

```bash
projects tree mon-projet -d 3 -a
```

## Icônes des fichiers

Le CLI utilise des emojis pour identifier visuellement les types de fichiers :

| Type | Icône | Extensions |
|------|-------|------------|
| Dossier | 📁 | - |
| Python | 🐍 | .py |
| JavaScript | 📜 | .js |
| TypeScript | 📘 | .ts |
| React | ⚛️ | .jsx, .tsx |
| Rust | 🦀 | .rs |
| Go | 🔵 | .go |
| Java | ☕ | .java |
| Markdown | 📝 | .md |
| JSON | 📋 | .json |
| Config | ⚙️ | .yaml, .yml, .toml |
| HTML | 🌐 | .html |
| CSS | 🎨 | .css, .svg |
| Shell | 🔧 | .sh |
| SQL | 🗄️ | .sql |
| Image | 🖼️ | .png, .jpg, .jpeg, .gif |
| Autre | 📄 | * |

## Dossiers ignorés

Par défaut, ces dossiers sont **automatiquement ignorés** :
- `.git`
- `__pycache__`
- `node_modules`
- `.venv`, `venv`
- `.idea`, `.vscode`
- `dist`, `build`
- `.next`, `.cache`
- `target`

Et ces fichiers :
- `*.pyc`
- `.DS_Store`

## Cas d'usage

### Explorer rapidement un nouveau projet

```bash
projects tree nouveau-projet -d 2
```

Donne un aperçu rapide de l'organisation.

### Vérifier la structure

```bash
projects tree mon-projet -d 3
```

Utile pour vérifier que ton projet est bien organisé.

### Inclure les configs cachées

```bash
projects tree mon-projet -d 1 --all
```

Pour voir les fichiers de configuration (`.env`, `.gitignore`, etc.)

## Prérequis

- Le projet doit avoir un **path** configuré
- Le path doit **exister** sur le système

## Erreurs courantes

### Projet non trouvé

```
✖ Project 'mon-projet' not found.
```

→ Vérifie avec `projects list`

### Pas de path

```
✖ Project 'mon-projet' has no path set.
```

→ Configure le path : `projects edit mon-projet --path /chemin`

### Path inexistant

```
✖ Path does not exist: /chemin/inexistant
```

→ Vérifie que le chemin est correct

## Voir aussi

- [info](info.md) - Informations du projet
- [git-tree](git-tree.md) - Arbre des commits Git (pas des fichiers)

---

**[← Retour aux commandes](../../COMMANDES.md)**
