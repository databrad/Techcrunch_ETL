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
```python 
def get_articles(category, max_load_more):
    driver = webdriver.Chrome()  # Utilisez le navigateur de votre choix (ici, Chrome)
    url = f"https://techcrunch.com/category/{category}/" #url où se trouvent les articles
    driver.get(url)
    reject_cookies_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Reject all')]")
    ActionChains(driver).move_to_element(reject_cookies_button).click().perform() # clique sur le bouton "Reject all"
    time.sleep(2) #attendre 2 secondes 
    i = 0
    
    articles = []
    while i<max_load_more:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        try:
            # Trouver et cliquer sur le bouton "LOAD MORE"
            load_more_button = driver.find_element(By.XPATH, "//button[contains(., 'Load More')]")
            ActionChains(driver).move_to_element(load_more_button).click().perform()
            i = i+1
            time.sleep(10)  # Attendre un peu après le clic pour que les nouveaux articles chargent (à régler en fonction de la connexion internet)
        except: 
        
            break
        ActionChains(driver).send_keys(Keys.ESCAPE).perform() # Fermer une fenêtre conceptuelle s'il y'en a (pop-up)
    #Récupération des données stockées dans des balises et classes spécifiques    
    for article, temps  in zip(soup.find_all("h2", class_="post-block__title"), 
                                       soup.find_all("div", class_="river-byline__full-date-time__wrapper")):
            
                title = article.find("a").text.strip()
                link = "https://techcrunch.com" + article.find("a")["href"]
                date_time = temps.find("time")["datetime"]
                articles.append({"title": title, "link": link, "date_time": date_time})
           
    driver.quit()
    return articles
```
Cette fonction get_articles utilise Selenium pour automatiser le navigateur, charger la page web et interagir avec les éléments de la page.
Elle recherche et clique sur le bouton "Reject all" pour rejeter les cookies, puis effectue plusieurs clics(max_load_more) sur le bouton "Load More" pour charger davantage d'articles. 
Elle utilise aussi BeautifulSoup pour extraire les titres, liens et dates des articles sur la catérogie (category).

# def get_article_details(article_url)
```python
def get_article_details(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    author = soup.find("div", class_="article__byline").find("a").text.strip()
    content = soup.find("div", class_="article-content").text.strip()
    
    return {"author": author, "content": content}
```
La fonction get_article_details récupère les détails d'un article en envoyant une requête HTTP à l'URL de l'article (récupérée à l'étape précédente), en analysant le contenu HTML de la page et en extrayant les informations pertinentes telles que l'auteur et le contenu de l'article.

```python
data = []
articles = get_articles(category, max_load)
for article in articles:
    article_details = get_article_details(article["link"])
    data.append({"Category": category, "Title": article["title"], "Link": article["link"],"Date_Time":article["date_time"], "Author": article_details["author"], "Content": article_details["content"]})
# Créer un DataFrame à partir des données
df = pd.DataFrame(data)
```
Les données extraitent sont à présent chargées dans une structure de données appellée Dataframe.

# def prepare_data(df)
```python
def prepare_data(df):
    df["Date"] = df["Date_Time"].map(lambda x: pd.to_datetime(x[:10])) #Récupère la date et converti en Timestamp
    df["Year"] = df["Date_Time"].map(lambda x: int(x[:4])) #Récupère l'année et converti en entier
    df["Month"] = df["Date_Time"].map(lambda x: int(x[5:7])) #Récupère le mois et converti en entier
    df["Day"] = df["Date_Time"].map(lambda x: int(x[8:10])) #Récupère le jour et converti en entier
    df["Content"] = df["Content"].map(lambda x: x.replace("\n"," ")) # remplace les caractères \n par un espace
    df = df.drop("Date_Time", axis=1) # supprime la colonne Date_Time
    return df

final_data = prepare_data(df)
```
La fonction prepare_data effectue plusieurs transformations sur le DataFrame pour extraire les informations de date, année, mois et jour à partir de la colonne "Date_Time". 
Elle nettoie également le contenu de la colonne "Content" en remplaçant les sauts de ligne par des espaces et finalement supprime la colonne "Date_Time" du DataFrame.

# def load_data(host, user, password, port, data)
```python
def load_data(host, user, password, port,data):
    #définir les paramètres pour la connexion à la base de données
    db_connection = mysql.connector.connect(
        host=host,  
        user=user,
        password=password,
        port=port  
    )
    print("connected")
    cursor = db_connection.cursor()
    create_db = "CREATE DATABASE IF NOT EXISTS techcrunch;" #création de la base de données
    use_db = "USE techcrunch;" #pointe sur la base de données
    #Création de la table
    create_query = " CREATE TABLE IF NOT EXISTS articles (id INT AUTO_INCREMENT PRIMARY KEY,category VARCHAR(255),title VARCHAR(511),link VARCHAR(255),author VARCHAR(255),content TEXT,date Date,year int,month int,day int	);"
    cursor.execute(create_db)
    cursor.execute(use_db)
    cursor.execute(create_query)
    # Charger les données dans la base de données
    for index, row in data.iterrows():
        insert_query = "INSERT INTO articles (category, title, link, author, content, date, year, month, day) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data_tuple = (row["Category"], row["Title"], row["Link"], row["Author"], row["Content"], row["Date"], row["Year"], row["Month"], row["Day"])
        cursor.execute(insert_query, data_tuple)

    db_connection.commit()
    cursor.close()
    db_connection.close()

    print("Données chargées dans la base de données MySQL.")

load_data("localhost", "root", "mysql_brad", "3306", final_data)
```
La fonction load_data se connecte à la base de données MySQL en utilisant les paramètres fournis, crée une base de données appelée "techcrunch" si elle n'existe pas déjà, utilise cette base de données, puis crée une table "articles" (si elle n'existe pas aussi) avec les colonnes appropriées. Ensuite, elle itère à travers les données préparées, construit et exécute les requêtes d'insertion SQL pour insérer les données dans la table "articles".


II. Le fichier scrapAPI.py pour créer une API et consommer le service.

```python
from flask import Flask, jsonify, request
import mysql.connector
app = Flask(__name__)
```

Ces lignes importent les bibliothèques nécessaires pour créer une application web Flask

```python
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mysql_brad",
    "database": "techcrunch"
}
```
Ces lignes définissent les détails de connexion à la base de données MySQL, tels que l'hôte (machine), l'utilisateur, le mot de passe et la base de données à utiliser.

```python
@app.route('/articles', methods=['GET'])
def get_articles():
    try:
        category = request.args.get('category')  
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor(dictionary=True)
                if category:
            query = "SELECT * FROM articles WHERE category = %s"
            cursor.execute(query, (category,))
        else:
            query = "SELECT * FROM articles"
            cursor.execute(query)

        articles = cursor.fetchall() #Afficher les articles 

        cursor.close()
        db_connection.close()

        return jsonify({"articles": articles})
    except Exception as e:
        return jsonify({"error": str(e)})
```
Cette partie définit une route pour l'URL /articles en utilisant la méthode GET. 
Lorsqu'un client effectue une requête GET à cette URL, la fonction get_articles sera exécutée. La fonction récupère le paramètre de requête category de l'URL (s'il est fourni) pour filtrer les articles par catégorie. 
Ensuite, une connexion à la base de données MySQL est établie en utilisant les informations de configuration définies précédemment.
En fonction de la présence ou de l'absence de la valeur category, la fonction exécute une requête SQL pour récupérer tous les articles correspondant à la catégorie donnée ou tous les articles, respectivement. 
Les résultats de la requête sont récupérés à l'aide de "cursor.fetchall()", puis la connexion et le curseur sont fermés.
Les données des articles sont renvoyées au client sous la forme d'une réponse JSON en utilisant la fonction "jsonify". 
Si une exception se produit lors de l'exécution de cette fonction, une réponse JSON contenant un message d'erreur est renvoyée.

```python
if __name__ == '__main__':
    app.run(debug=True)
```

Cette ligne vérifie si le script est exécuté en tant que programme principal, c'est-à-dire si c'est le fichier qui est exécuté directement. 
Si c'est le cas, l'application Flask est lancée en mode de débogage avec l'option debug=True. Cela signifie que si une erreur se produit, des informations de débogage détaillées seront affichées dans le navigateur.

III. Utilisation

1. scraper.py :
   pour scrapper les articles liés à la catégorie "venture" en chargeant la page 2 fois (max_load_more = 2) : py scraper.py venture 2

2. L'API:
   L'appel de l'api se fait sur un consommateur web ou un navigateur web.
   Il faut lancer le serveur sql (base de données) au préalble.
   Pour récupérer tous les articles: http://localhost:5000/articles
   pour récupérer les articles de la catégory security: http://localhost:5000/articles?category=security (Il faut au préalable scrapper les articles sur la catégorie "security")



