# Discord ConvoTalk

Un clone Discord complet avec chat temps réel, authentification, et gestion des canaux.

## Fonctionnalités

- 🔐 Authentification complète (register/login + Google OAuth)
- 💬 Chat en temps réel avec WebSockets
- 🏠 Gestion des canaux et messages
- 👥 Utilisateurs en ligne
- 📱 Interface responsive Discord-like
- 🛡️ Sécurité JWT et sessions

## Tech Stack

- **Frontend**: React 19, Tailwind CSS, Socket.io-client
- **Backend**: FastAPI, Python, WebSockets
- **Database**: MongoDB (Atlas)
- **Deployment**: Render (gratuit)

## Déploiement

Cette application est déployée sur Render avec MongoDB Atlas.

### Variables d'environnement

```
MONGO_URL=mongodb+srv://...
DB_NAME=discord_clone_db
JWT_SECRET=your_jwt_secret
CORS_ORIGINS=*
```

## Installation locale

1. Backend:
```bash
cd backend
pip install -r requirements.txt
python server.py
```

2. Frontend:
```bash
cd frontend
yarn install
yarn start
```

## Auteur

Clone Discord créé avec Emergent.sh