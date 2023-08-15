# Techcrunch_ETL
Une ETL et une API pour récupérer les articles du site techcrunch.com


I. Le fichier scraper.py pour scraper les articles du site.

#importation des librairies
1. selenium: Utilisée pour l'automatisation du navigateur web (Chromedriver dans ce cas) afin de récupérer les données du site.
2. BeautifulSoup: Utilisée pour analyser le contenu HTML et extraire les informations souhaitées.
3. time: Utilisée pour ajouter des délais pendant l'exécution du script. (en seconde)
4. requests: Utilisée pour envoyer des requêtes HTTP pour récupérer le contenu d'une page.
5. pandas: Utilisée pour créer et manipuler des DataFrames.
6. sys: Utilisée pour accéder aux arguments de la ligne de commande.
7. mysql.connector: Utilisée pour la communication avec la base de données MySQL.

# def get_articles(category, max_load_more)
Cette fonction get_articles utilise Selenium pour automatiser le navigateur, charger la page web et interagir avec les éléments de la page.
Elle recherche et clique sur le bouton "Reject all" pour rejeter les cookies, puis effectue plusieurs clics(max_load_more) sur le bouton "Load More" pour charger davantage d'articles. 
Elle utilise aussi BeautifulSoup pour extraire les titres, liens et dates des articles sur la catérogie (category).

# def get_article_details(article_url)
La fonction get_article_details récupère les détails d'un article en envoyant une requête HTTP à l'URL de l'article (récupérée à l'étape précédente), en analysant le contenu HTML de la page et en extrayant les informations pertinentes telles que l'auteur et le contenu de l'article.
Ensuite, Les données extraitent sont chargées dans une structure de données appellée Dataframe.

# def prepare_data(df)
La fonction prepare_data effectue plusieurs transformations sur le DataFrame pour extraire les informations de date, année, mois et jour à partir de la colonne "Date_Time". 
Elle nettoie également le contenu de la colonne "Content" en remplaçant les sauts de ligne par des espaces et finalement supprime la colonne "Date_Time" du DataFrame.

# def load_data(host, user, password, port, data)
La fonction load_data se connecte à la base de données MySQL en utilisant les paramètres fournis, crée une base de données appelée "techcrunch" si elle n'existe pas déjà, utilise cette base de données, puis crée une table "articles" (si elle n'existe pas aussi) avec les colonnes appropriées. Ensuite, elle itère à travers les données préparées, construit et exécute les requêtes d'insertion SQL pour insérer les données dans la table "articles".


II. Le fichier scrapAPI.py pour créer une API et consommer le service.

#importation des bibliothèques
1. flask: pour la création de notre API

Définition des détails de connexion à la base de données MySQL, tels que l'hôte (machine), l'utilisateur, le mot de passe et la base de données à utiliser.

Défintion d'une route pour l'URL /articles en utilisant la méthode GET. 
Lorsqu'un client effectue une requête GET à cette URL, la fonction get_articles sera exécutée. La fonction récupère le paramètre de requête category de l'URL (s'il est fourni) pour filtrer les articles par catégorie. 
Ensuite, une connexion à la base de données MySQL est établie en utilisant les informations de configuration définies précédemment.
En fonction de la présence ou de l'absence de la valeur category, la fonction exécute une requête SQL pour récupérer tous les articles correspondant à la catégorie donnée ou tous les articles, respectivement. 
Les résultats de la requête sont récupérés à l'aide de "cursor.fetchall()", puis la connexion et le curseur sont fermés.
Les données des articles sont renvoyées au client sous la forme d'une réponse JSON en utilisant la fonction "jsonify". 
Si une exception se produit lors de l'exécution de cette fonction, une réponse JSON contenant un message d'erreur est renvoyée.

Le code vérifie si le script est exécuté en tant que programme principal, c'est-à-dire si c'est le fichier qui est exécuté directement. 
Si c'est le cas, l'application Flask est lancée en mode de débogage avec l'option debug=True. Cela signifie que si une erreur se produit, des informations de débogage détaillées seront affichées dans le navigateur.

III. Utilisation

1. scraper.py :
   pour scrapper les articles liés à la catégorie "venture" en chargeant la page 2 fois (max_load_more = 2) : py scraper.py venture 2

2. L'API:
   L'appel de l'api se fait sur un consommateur web ou un navigateur web.
   Il faut lancer le serveur sql (base de données) au préalble.
   Pour récupérer tous les articles: http://localhost:5000/articles
   pour récupérer les articles de la catégory security: http://localhost:5000/articles?category=security (Il faut au préalable scrapper les articles sur la catégorie "security")



