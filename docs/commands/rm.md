# rm - Supprimer un projet

Supprime un projet de la base de données.

## Synopsis

```bash
projects rm <nom>
```

## Exemple

```bash
projects rm vieux-projet
```

Demande confirmation :
```
Are you sure you want to delete 'vieux-projet'? [y/N]: y
✔ Project 'vieux-projet' deleted.
```

⚠️ **Attention** : Cette action est irréversible ! Le projet sera supprimé de la base de données (mais pas du disque).

## Voir aussi

- [list](list.md) - Lister les projets
- [stale](stale.md) - Trouver les projets à supprimer

---

**[← Retour aux commandes](../../COMMANDES.md)**
