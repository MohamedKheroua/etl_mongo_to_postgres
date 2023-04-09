  <h2 align="center">Mise en place d'un pipeline ETL depuis une base MongoDB</h2>

<br />

### **À propos du projet**

Une enseigne de jeux vidéos cherche à améliorer son catalogue de vente en ligne. Pour cela, elle veut proposer sur sa page d’accueil et dans ses campagnes de communication (newsletter, réseaux sociaux) une **liste des jeux les mieux notés et les plus appréciés** de la communauté sur les derniers jours.

Afin de refléter au mieux l’avis des internautes, elle souhaite **récupérer les avis les plus récents** de ses propres clients en ligne pour déterminer les jeux les mieux notés. Les développeurs Web de l’entreprise souhaitent pouvoir requêter ces informations sur une base de données SQL qui va historiser au jour le jour les jeux les mieux notés.

Les données brutes sont stockées dans une base MongoDB et il est supposé que celles-ci sont ajoutées au fur et à mesure par d’autres programmes (API backend). L’objectif est de construire un pipeline de données qui va alimenter automatiquement un Data Warehouse (représenté par une base de données SQL) tous les jours en utilisant les données depuis la base MongoDB.

<br />

### **Étapes du projet**

&#10004; Ajouter les données brutes dans une base MongoDB

&#10004; Créer la base de données SQL avec le schéma associé

&#10004; Développer le script Python du pipeline ETL

&#10004; Automatiser le pipeline avec un outil de planification

<br />

### **Structure du projet**

Le dépôt Git contient les éléments suivantes.

- `data/` contient les données du projet
- `src/` contient les codes sources Python principaux du projet
- `mongodb/` contient le fichier YAML de configuration pour le déploiement des containers Docker
- `postgres/` contient le fichier de configuration contenant les paramètres de connexion à la bdd PostgreSQL
- `LICENSE.txt` : licence du projet
- `README.md` : fichier d'accueil
- `requirements.txt` : liste des dépendances Python nécessaires

<br />

### **Configuration de l'environnement de travail**

Les instructions suivantes permettent de configurer l'environnement de travail et de créer un envi le projet sur sa machine.

### Pré-requis

- <a href="https://www.python.org/downloads/">Python 3</a>

- <a href="https://www.docker.com/products/docker-desktop/">Docker</a>

### Installation

1. Cloner le projet Git

	```
	git clone https://github.com/
	```

2. Installer les clients MongoDB et PostgreSQL

	L'installation peut se faire en local ou sur des serveurs dédiés sur le cloud (par exemple sur des instances EC2 sur AWS ou des clusters Dataproc sur GCP).

	Voici les procédures que l'on pourra suivre pour l'installation en local :

	- MongoDB
	
		On pourra passer par l'utilisation de containers à partir de :
		- l'image Docker <a href="https://hub.docker.com/_/mongo">mongo</a> pour le client MongoDB
		- l'image Docker <a href="https://hub.docker.com/_/mongo-express">mongo-express</a>, pour l'interface Web d'administration des bases de données MongoDB

		Le fichier YAML `docker-compose.yml` du dossier `mongodb` permet de déploier facilement les deux containers Docker.

	<br />

	- PostgreSQL

		Les packages d'installation sont disponibles à cette <a href="https://www.postgresql.org/download/">adresse</a>.

		On pourra également installer <a href="https://www.pgadmin.org/">pgAdmin</a> qui est un outil opensource d'administration des bases de données PostgreSQL.


3. Installer les dépendances du fichier `requirements.txt` dans un environnement virtuel

	*Linux / MacOS / WSL*
	```
	python3 -m venv venv/
	source venv/bin/activate
	pip install -r requirements.txt
	```
	*Windows*
	```
	python3 -m venv venv/
	C:\<chemin_dossir>\venv\Scripts\activate.bat
	pip install -r requirements.txt
	```

4. Paramétrage d'Apache Airflow

	Apache Airflow est utilisé sur le projet pour automatiser les pipelines de données. La version utilisée est spécifiée dans le fichier `requirements.txt` .

	Avant de pouvoir l'utiliser pour exécuter nos workfows, un minimum de paramétrage sera nécessaire.

	On pourra suivre la procédure détaillée dans le fichier `setup_airflow.md` . 

<br />

### **Démarrage**

- #### **Création de la base de données dans MongoDB**
 
	On pourra utiliser le client web mongo-express pour créer notre base de données et la collection que l'on utilisera par la suite.

	L'URL d'accès (par défaut) en local est la suivante : <a href="http://localhost:8081/">localhost:8081</a>

- #### **Ingestion des données brutes dans MongoDB**

	Les données brutes compressées peuvent être récupérées à cette <a href="https://drive.google.com/file/d/1bJoEcxSQ-t64NRz8a6tYX46TpZVBzWsk/view?usp=sharing">adresse</a>.

	Elles seront utilisées pour alimenter la base de données MongoDB avec le script `raw_data_ingestion.py` .

- #### **Création de la base de données cible dans PostgreSQL**
	
	On pourra utiliser pgAdmin pour créer notre base de données.
	
- #### **ETL MongoDB vers PostgreSQL**

	On pourra dans un premier temps utiliser le script `raw_data_ingestion.py` pour tester le pipeline.

	En complément des variables d'environnement spécifiées dans le fichier de configuration `database.ini` du dossier `config`, les variables d'environnement `MONGODB_USERNAME` et `MONGODB_PASSWORD` sont utilisées pour accéder aux bases de données MongoDB, ces deux dernières ayant les valeurs par défaut spécifiées dans le fichier YAML `docker-compose.yml` (à modifier si besoin).

	Il faudra penser à créer toutes les variables d'environnement utilisées dans le projet avant de lancer les scripts Python (ou modifier le code).

- #### **Automatisation avec Airflow**

	Deux DAG Airflow sont disponibles pour automatiser le lancement quotidien des pipelines ETL :

		- ttes

### **Licence**

*Données mises à disposition par <a href="https://blent.ai">Blent.ai</a>. Les données utilisées pour ce projet peuvent être soumises à des droits d'auteur et de propriété intellectuelle. Blent.ai ne peut être responsable des utilisations faites des données utilisées dans le cadre de ce projet.*