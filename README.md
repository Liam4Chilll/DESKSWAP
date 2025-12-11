# 🗂️ Desk Swap v2.0

**Gestionnaire de fichiers simple, rapide et sécurisé pour environnements Docker**

Desk Swap est un gestionnaire de fichiers web léger conçu pour les conteneurs Docker. Parcourez, téléchargez et gérez vos fichiers depuis votre serveur via une interface web élégante.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)

## ✨ Fonctionnalités

- 📁 **Navigation intuitive** - Parcourez les dossiers avec fil d'Ariane
- 📥 **Téléchargements multiples** - Fichiers uniques, sélection multiple ou dossiers complets en ZIP
- 🔒 **Sécurisé par conception** - Accès lecture seule, validation des chemins, isolation conteneur
- 🎨 **Interface épurée** - Design moderne et responsive sur tous les appareils
- ⚡ **Ultra-léger** - Base Alpine Linux, dépendances minimales
- 🐳 **Docker Ready** - Déploiement en une seule commande

## 🚀 Démarrage rapide

### Prérequis

- Docker
- Docker Compose

### Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/liam4chilll/DESKSWAP.git
cd deskswap
```

2. Configurez votre dossier dans `docker-compose.yml` :
```yaml
volumes:
  - /votre/dossier:/data:ro  # Changez /votre/dossier
```

3. Démarrez le service :
```bash
docker compose up -d
```

4. Accédez à l'interface :
```
http://localhost:8080
```

C'est tout ! 🎉

## 📋 Configuration

### Changer le port

Éditez `docker-compose.yml` :
```yaml
ports:
  - "8080:8080"  # Changez le premier port (hôte:conteneur)
```

### Changer le dossier racine

1. Mettez à jour le volume dans `docker-compose.yml` :
```yaml
volumes:
  - /nouveau/chemin:/data:ro
```

2. Mettez à jour `ROOT_PATH` dans `app.py` :
```python
ROOT_PATH = '/data'
```

### Variables d'environnement

Variables disponibles :

| Variable | Description | Défaut |
|----------|-------------|---------|
| `FLASK_PORT` | Port du serveur | `8080` |
| `ROOT_PATH` | Chemin du dossier racine | `/data` |

## 🎯 Cas d'usage

- **Équipes dev** - Partage de fichiers projet entre membres
- **DevOps** - Accès rapide aux logs et configurations
- **Home Lab** - Gestion de fichiers sur serveur personnel
- **Accès backups** - Téléchargement de sauvegardes
- **Distribution fichiers** - Partage sécurisé avec collègues

## 🛡️ Fonctionnalités de sécurité

- ✅ Accès système de fichiers en lecture seule
- ✅ Protection contre traversée de chemin
- ✅ Isolation conteneur
- ✅ Pas d'authentification par défaut (conçu pour réseaux sécurisés)
- ✅ Surface d'attaque minimale

**Note** : Desk Swap est conçu pour réseaux de confiance. Pour exposition Internet, ajoutez une authentification via reverse proxy (nginx, Traefik, Caddy).

## 📖 Utilisation

### Navigation
- Cliquez sur les dossiers pour naviguer
- Utilisez le fil d'Ariane pour revenir en arrière
- Cliquez sur les noms de fichiers pour prévisualiser (si supporté)

### Téléchargement
- **Fichier unique** : Cliquez sur "Télécharger"
- **Dossier en ZIP** : Cliquez sur "ZIP" à côté du dossier
- **Sélection multiple** : Cochez les cases, cliquez "Télécharger la sélection"
- **Tout télécharger** : Cliquez sur "Tout télécharger (ZIP)"

## 🏗️ Architecture

```
deskswap/
├── app.py              # Application Flask
├── templates/
│   └── index.html      # Interface web
├── Dockerfile          # Image conteneur
├── docker-compose.yml  # Configuration déploiement
└── README.md           # Documentation
```

**Stack technique** :
- Backend : Python 3.11 + Flask
- Frontend : HTML/CSS/JavaScript vanilla
- Conteneur : Alpine Linux
- Serveur : Gunicorn (production) / Flask dev server

## 🔧 Développement

### Développement local

```bash
# Installer les dépendances
pip install flask

# Lancer localement
python app.py

# Accéder à http://localhost:8080
```

### Construction image personnalisée

```bash
docker build -t deskswap:custom .
docker run -p 8080:8080 -v /votre/chemin:/data:ro deskswap:custom
```

## 📊 Performance

- **Taille conteneur** : ~50MB
- **Utilisation mémoire** : ~30MB au repos
- **Temps démarrage** : <2 secondes
- **Utilisateurs simultanés** : 50+ (config par défaut)

## 🤝 Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à soumettre une Pull Request.

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## ⭐ Historique des étoiles

Si vous trouvez Desk Swap utile, pensez à lui donner une étoile sur GitHub !


*Desk Swap v1.0 - Gestion de fichiers simple en lab*
