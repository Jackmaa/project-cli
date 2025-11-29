# tag - Gérer les tags

Ajoute, supprime ou affiche les tags d'un projet.

## Synopsis

```bash
projects tag <nom> [OPTIONS]
```

## Arguments

| Argument | Type | Description |
|----------|------|-------------|
| `nom` | string | Nom du projet (obligatoire) |

## Options

| Option | Raccourci | Type | Description |
|--------|-----------|------|-------------|
| `--add` | `-a` | string | Tags à ajouter (séparés par des virgules) |
| `--remove` | `-r` | string | Tags à supprimer (séparés par des virgules) |

## Exemples

### Voir les tags actuels

```bash
projects tag mon-projet
```

Affiche :
```
ℹ Current tags for 'mon-projet': web, react, typescript
```

### Ajouter des tags

Un seul tag :
```bash
projects tag mon-projet --add "frontend"
# ou
projects tag mon-projet -a "frontend"
```

Plusieurs tags :
```bash
projects tag mon-projet -a "web,react,typescript,nextjs"
```

⚠️ **Attention à l'ordre** : le nom du projet vient **avant** les options !

```bash
# ✅ Correct
projects tag mon-projet -a "Vue.js"

# ❌ Incorrect
projects tag -a mon-projet "Vue.js"
```

### Supprimer des tags

```bash
projects tag mon-projet --remove "old-tag"
# ou
projects tag mon-projet -r "old-tag,deprecated"
```

### Ajouter ET supprimer

```bash
projects tag mon-projet -a "new-tag" -r "old-tag"
```

## Cas d'usage

### Organisation par langage

```bash
projects tag web-app -a "javascript,typescript"
projects tag api-backend -a "python,fastapi"
projects tag game-project -a "rust,gamedev"
```

Puis filtrer :
```bash
projects list --tag python
```

### Organisation par type

```bash
projects tag portfolio -a "web,frontend,personal"
projects tag cli-tool -a "cli,tool,utility"
projects tag api -a "backend,api,rest"
```

### Organisation par framework

```bash
projects tag dashboard -a "react,nextjs,tailwind"
projects tag blog -a "vue,nuxt,markdown"
```

### Organisation par contexte

```bash
projects tag side-project -a "personal,fun,learning"
projects tag client-work -a "professional,client,urgent"
```

## Format des tags

- **Séparateur** : virgule `,`
- **Espaces** : automatiquement supprimés
- **Casse** : respectée (attention : `Python` ≠ `python`)

```bash
# Ces deux commandes sont équivalentes
projects tag projet -a "web, react, frontend"
projects tag projet -a "web,react,frontend"
```

## Conseils

💡 **Utilise une convention** : décide si tu utilises des minuscules, des tirets, etc.

Exemples de conventions :
```bash
# Tout en minuscules
projects tag projet -a "react,typescript,web"

# Avec tirets
projects tag projet -a "react-native,mobile-app"

# Avec majuscules pour les noms propres
projects tag projet -a "React,TypeScript,Node.js"
```

💡 **Sois cohérent** pour faciliter les filtres :

```bash
# ✅ Bon - cohérent
projects tag app1 -a "python,fastapi,postgresql"
projects tag app2 -a "python,django,postgresql"
projects list --tag python  # Trouve les deux

# ❌ Moins bon - incohérent
projects tag app1 -a "Python,FastAPI,PostgreSQL"
projects tag app2 -a "python,django,postgres"
projects list --tag python  # Ne trouve que app2
```

## Voir aussi

- [list](list.md) - Filtrer par tag
- [add](add.md) - Ajouter des tags lors de la création

---

**[← Retour aux commandes](../../COMMANDES.md)**
