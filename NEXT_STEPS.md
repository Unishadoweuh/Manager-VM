# ✅ PROBLÈME RÉSOLU - Prochaines étapes

## Ce qui a été fait

Le `package-lock.json` a été généré avec succès dans le dossier `frontend/`.

## Sur votre serveur Linux (root@Manager-VM)

### 1. Copier le package-lock.json vers le serveur

Depuis Windows, copiez le fichier vers votre serveur :

```powershell
# Option 1: SCP (si vous avez OpenSSH)
scp F:\Bureau\Manager-VM\frontend\package-lock.json root@Manager-VM:/opt/Manager-VM/frontend/

# Option 2: Manuellement via WinSCP, FileZilla, etc.
```

### 2. Sur le serveur, rebuild et démarrer

```bash
cd /opt/Manager-VM
docker compose up -d --build
```

Cela devrait maintenant fonctionner car `package-lock.json` existe.

## ⏱️ Temps d'attente estimé

- **Build backend**: ~2-3 minutes
- **Build frontend**: ~3-5 minutes  
- **Démarrage services**: ~30-60 secondes
- **Total**: ~6-9 minutes

## 📊 Vérification après démarrage

```bash
# Voir l'état des services
docker compose ps

# Devrait afficher 6 services "healthy" ou "running":
# - postgres (healthy)
# - redis (healthy)
# - backend (healthy)
# - celery-worker (running)
# - celery-beat (running)
# - frontend (healthy)
# - caddy (healthy)
```

## 🔍 Logs en temps réel

```bash
# Tous les services
docker compose logs -f

# Un service spécifique
docker compose logs -f backend
docker compose logs -f frontend
```

## ✅ Tests après démarrage

### 1. Backend API

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Devrait retourner: {"status":"ok"}
```

### 2. Frontend

```bash
# Accéder depuis le serveur
curl http://localhost:3000

# Ou depuis votre navigateur
http://<ip-du-serveur>:3000
```

### 3. Créer l'admin

```bash
docker compose exec backend python -m app.scripts.create_admin
```

### 4. Seed la base (optionnel)

```bash
docker compose exec backend python -m app.scripts.seed_db
```

## 🎯 Accès à l'application

Une fois démarrée :

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/v1/docs
- **Login**: Utiliser `FIRST_ADMIN_EMAIL` et `FIRST_ADMIN_PASSWORD` du `.env`

## 🐛 En cas d'erreur

### Backend ne démarre pas

```bash
# Voir les logs
docker compose logs backend

# Erreurs communes:
# - Database not ready → Attendre 30s de plus
# - Migration failed → docker compose exec backend alembic upgrade head
```

### Frontend ne démarre pas

```bash
# Voir les logs
docker compose logs frontend

# Rebuild si nécessaire
docker compose build frontend --no-cache
docker compose up -d frontend
```

### Port déjà utilisé

```bash
# Vérifier les ports
netstat -tulpn | grep -E ':(3000|8000|5432|6379|80|443)'

# Modifier dans docker-compose.yml si conflit
```

## 📋 Prochaines étapes après démarrage

1. ✅ Accéder au frontend sur http://localhost:3000
2. ✅ Login avec les credentials admin
3. ✅ Ajouter un serveur Proxmox (Admin → Servers)
4. ✅ Créer des templates (Admin → Templates)
5. ✅ Créer un utilisateur test
6. ✅ Ajouter des crédits à l'utilisateur
7. ✅ Tester la création d'une VM

## 📞 Support

Si vous rencontrez des problèmes :

1. Vérifier les logs : `docker compose logs -f`
2. Vérifier l'état : `docker compose ps`
3. Consulter la documentation : `docs/ADMIN_GUIDE.md`
4. Consulter le troubleshooting : `README.md` section 🚨

---

**Status**: Frontend package-lock.json ✅ | Prêt pour `docker compose up -d --build` sur le serveur
