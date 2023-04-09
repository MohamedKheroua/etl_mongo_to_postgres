<h2 align="center">Procédure d'installation d'Apache Airflow</h2>

<br />

### **À propos**

On pourra suivre cette procédure pour installer et paramétrer Airflow avant la première utilisation.

<br />

### **Configuration de l'environnement de travail**

Les instructions suivantes permettent de configurer l'environnement de travail et de créer un envi le projet sur sa machine.

### Pré-requis

- Python 3

- {Visual Studio Code + distribution WSL2} ou Linux

### Installation

1. Créer le dossier apache_airflow
    
    On pourra créer un nouveau dossier de projet dédié à Airflow dans notre dossier de travail (par exemple nommé `apache_airflow`) :

	```
	mkdir apache_airflow
	```

    *Remarque :*

    *Apache Airflow pourra être utilisé communément par plusieurs projets différents ; il est donc préférable de créer le répertoire `apache_airflow` à la racine de notre dossier de travail global et non pas dans un répertoire de projet spécifique.*

<br/>

2. Créer un environnement virtuel dédié dans le nouveau dossier créé

    ```
    python3 -m venv venv
    ```

3. Activer l'environnement virtuel et y installer Airflow

    Il faudra copier le fichier `requirements.txt` dans le dossier avant de pouvoir installer les dépendances :

    ```
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

4. Créer le dossier Airflow

    ```
    mkdir airflow
    ```

5. Définir la variable d'environnement `AIRFLOW_HOME`

    Il est très important de toujours définir la variable d'environnement `AIRFLOW_HOME`, sinon Airflow ira par défaut dans le répertoire utilisateur et ne trouvera pas les fichiers associés (modifier la commande pour y ajouter le bon chemin de dossier):

    ```
    export AIRFLOW_HOME=<PATH_DE_MON_DOSSIER_DE_TRAVAIL>/apache_airflow/airflow
    ```

6. Modifier le fichier `~/.bashrc` pour y ajouter la variable d'environnement `AIRFLOW_HOME`

    Cela permettra de créer la variable d'environnement à chaque redémarrage ou ouverture d'un nouveau terminal :

    ```
    echo 'export AIRFLOW_HOME=<PATH_DE_MON_DOSSIER_DE_TRAVAIL>/apache_airflow/airflow' >> ~/.bashrc 
    ```

7. Initialiser la base de données d'Airflow

    ```
    airflow db init 
    ```

    Si tout a fonctionné, plusieurs fichiers ont été créés dans le dossier `airflow/` :

    - la base de données `airflow.db` au format SQLite
    - le fichier de configuration `airflow.cfg`
    - le fichier spécifique au Web Server `webserver_config.py`

<br/>

8. Créer un utilisateur

    Depuis les versions 2.+, un utilisateur par défaut est obligatoire pour pouvoir accéder à l'interface (modifier les valeurs des paramètres avant de lancer la commande):

    ```
    airflow users create \
    --username John \
    --firstname John \
    --lastname Doe \
    --role Admin \
    --email john.dow@myemail.com
    ```

    Un mot de passe sera demandé pour confirmer l'ajout du nouvel utilisateur.

9. Création du script `scheduler.sh` dans le dossier `apache_airflow`

    Ce script sera nécessaire pour exécuter le scheduler d'Airflow. Il faudra créer le fichier puis y copier les lignes suivantes :

    ```
    export AIRFLOW_HOME=<PATH_DE_MON_DOSSIER_DE_TRAVAIL>/apache_airflow/airflow
    airflow scheduler
    ```

10. Création du script `webserver.sh` dans le dossier `apache_airflow`

    Ce script sera nécessaire pour exécuter le webserver d'Airflow. Il faudra créer le fichier puis y copier les lignes suivantes :

    ```
    export AIRFLOW_HOME=<PATH_DE_MON_DOSSIER_DE_TRAVAIL>/apache_airflow/airflow
    airflow webserver
    ```

11. Modifier les autorisations d'exécution des deux fichiers

    Cela est nécessaire pour donner les droits d'accès en exécution sur les deux fichiers nouvellement créés :

    ```
    chmod 744 scheduler.sh
    chmod 744 webserver.sh
    ```

12. Ouvrir deux nouveaux terminaux pour lancer les deux scripts `scheduler.sh` et `webserver.sh`

    On active l'environnement virtuel dans les deux nouveaux terminaux avant d'exécuter les scripts :

    Pour le premer terminal :

    ```
    source venv/bin/activate
    ./scheduler.sh
    ```

    Pour le deuxième terminal :

    ```
    source venv/bin/activate
    ./webserver.sh
    ```

13. Ouvrir deux nouveaux terminaux pour lancer les deux scripts `scheduler.sh` et `webserver.sh`

    On active l'environnement virtuel dans les deux nouveaux terminaux avant d'exécuter les scripts :

    Pour le premer terminal :

    ```
    source venv/bin/activate
    ./scheduler.sh
    ```

    Si tout a fonctionné, l'accès à l'interface administrateur d'Airflow est disponible depuis <a href="http://localhost:8080">cette adresse</a>.

    On pourra y voir tous les exemples de DAGs présents par défaut.

<br/>

14. Créer un nouveau dossier `dags` dans le dossier `airflow`

    Ce dossier contiendra tous nos futurs DAGs :

    ```
    mkdir dags
    ```

    Lors du prochain lancement du scheduler, les DAGs ajoutés dans ce dossier seront visibles depuis l'interface web, avec les DAGs présents par défaut.

<br/>

15. Commandes pour lancer un DAG

    On pourra utiliser les backfills pour lancer nos DAGs. Par exemple, si on exécute le backfill suivant :

    ```
    airflow dags backfill mon_exemple_de_dag -s 2023-04-01 -e 2023-04-03
    ```

    le DAG `mon_exemple_de_dag` sera exécuté entre le 01/04/2023 (paramètre `-s` pour "start") et le 03/04/2023 (paramètre `-e` pour "end") : il y aura donc trois exécutions.

    On peut également nettoyer un backfill, en spécifiant la fenêtre temporelle visée. Par exemple :

    ```
    airflow tasks clear mon_exemple_de_dag -s 2023-04-02 -e 2023-04-02
    ```

