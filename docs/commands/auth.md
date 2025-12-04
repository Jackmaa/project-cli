# Commande `auth`

## Description

Gérer les tokens d'authentification pour GitHub et GitLab de manière sécurisée.

## Usage

```bash
projects auth PLATFORM [OPTIONS]
```

## Arguments

- `PLATFORM` - Plateforme : 'github' ou 'gitlab'

## Options

- `--token, -t TEXT` - Token API à stocker
- `--delete, -d` - Supprimer le token stocké
- `--show, -s` - Afficher le statut du token
- `--test` - Tester la validité du token
- `--list, -l` - Lister toutes les plateformes avec tokens
- `--method, -m TEXT` - Méthode de stockage: 'keyring', 'encrypted_file', ou 'both' (défaut: both)

## Exemples

### Stocker un token GitHub

```bash
# Méthode interactive (recommandée - masque le token)
projects auth github
# Entre ton token quand demandé

# Avec l'option --token
projects auth github --token ghp_xxxxxxxxxxxxx

# Stocker uniquement dans le keyring (plus sécurisé)
projects auth github --token ghp_xxxxxxxxxxxxx --method keyring
```

### Afficher le statut

```bash
# Afficher le token (masqué)
projects auth github --show

# Lister toutes les plateformes avec tokens
projects auth --list
```

### Tester la validité

```bash
# Vérifier si le token fonctionne
projects auth github --test
```

### Supprimer un token

```bash
# Supprimer le token de tous les emplacements
projects auth github --delete
```

## Sécurité

Le système utilise une approche hybride pour le stockage des tokens :

### 1. Keyring système (par défaut)
- **Linux**: SecretStorage (GNOME Keyring, KWallet)
- **macOS**: Keychain
- **Windows**: Windows Credential Locker
- Chiffrement au niveau de l'OS
- Protégé par ton mot de passe de session

### 2. Fichier chiffré (fallback)
- Stocké dans `~/.config/project-cli/.tokens`
- Chiffré avec AES-128 (Fernet)
- Permissions `600` (lecture/écriture propriétaire uniquement)

### 3. Variable d'environnement
- `GITHUB_TOKEN` ou `GITLAB_TOKEN`
- Utile pour CI/CD
- Aucun stockage persistant

## Workflow recommandé

```bash
# 1. Créer un token sur GitHub
#    https://github.com/settings/tokens
#    Permissions: repo (Full control of private repositories)

# 2. Stocker le token
projects auth github --token ghp_xxxxxxxxxxxxx

# 3. Tester le token
projects auth github --test

# 4. Utiliser avec sync
projects sync enable monprojet
projects sync run monprojet
```

## Permissions requises

### GitHub
- `repo` - Accès complet aux repos (publics et privés)
- `workflow` - Pour lire les statuts CI/CD (optionnel)

### GitLab
- `read_api` - Lecture via API
- `read_repository` - Lecture des repos

## Dépannage

### Token invalide
```bash
projects auth github --test
# Si échec: vérifie que le token n'est pas expiré sur GitHub
```

### Problème de keyring
```bash
# Utiliser uniquement le fichier chiffré
projects auth github --token XXX --method encrypted_file
```

### Rate limit dépassé
```bash
# Vérifier les limites API
projects sync rate-limit github
```

---

**[← Retour aux commandes](../../COMMANDES.md)**
