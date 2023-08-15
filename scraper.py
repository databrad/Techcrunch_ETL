# Importation des librairies à utiliser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import requests
import pandas as pd
import sys
import mysql.connector


# Utilisation
if len(sys.argv) < 3:
    print("Utilisation: python scrap.py <category> <max_load_more>")
    sys.exit(1)

# récupération des arguments passés en ligne de commande
category = sys.argv[1]
max_load = int(sys.argv[2])


# étape EXTRACT de l'ETL
# ===================================================================================================================================================
def get_articles(category, max_load_more):
    driver = webdriver.Chrome()  # Interaction avec le navigateur Chrome
    url = f"https://techcrunch.com/category/{category}/"  # url où se trouvent les articles
    driver.get(url)
    reject_cookies_button = driver.find_element(
        By.XPATH, "//button[contains(text(), 'Reject all')]"
    )
    ActionChains(driver).move_to_element(
        reject_cookies_button
    ).click().perform()  # clique sur le bouton "Reject all"
    time.sleep(2)  # attendre 2 secondes
    i = 0

    articles = []
    while i < max_load_more:
        soup = BeautifulSoup(driver.page_source, "html.parser")

        try:
            # Trouver et cliquer sur le bouton "LOAD MORE"
            load_more_button = driver.find_element(
                By.XPATH, "//button[contains(., 'Load More')]"
            )
            ActionChains(driver).move_to_element(load_more_button).click().perform()
            i = i + 1
            time.sleep(
                10
            )  # Attendre un peu après le clic pour que les nouveaux articles chargent (à régler en fonction de la connexion internet)
        except:
            break
        ActionChains(driver).send_keys(
            Keys.ESCAPE
        ).perform()  # Fermer une fenêtre conceptuelle s'il y'en a (pop-up)
    # Récupération des données stockées dans des balises et classes spécifiques
    for article, temps in zip(
        soup.find_all("h2", class_="post-block__title"),
        soup.find_all("div", class_="river-byline__full-date-time__wrapper"),
    ):
        title = article.find("a").text.strip()
        link = "https://techcrunch.com" + article.find("a")["href"]
        date_time = temps.find("time")["datetime"]
        articles.append({"title": title, "link": link, "date_time": date_time})

    driver.quit()
    return articles


# Fonction pour récupérer les détails d'un article
def get_article_details(article_url):
    response = requests.get(article_url)
    soup = BeautifulSoup(response.content, "html.parser")

    author = soup.find("div", class_="article__byline").find("a").text.strip()
    content = soup.find("div", class_="article-content").text.strip()

    return {"author": author, "content": content}


data = []

articles = get_articles(category, max_load)
for article in articles:
    article_details = get_article_details(article["link"])
    data.append(
        {
            "Category": category,
            "Title": article["title"],
            "Link": article["link"],
            "Date_Time": article["date_time"],
            "Author": article_details["author"],
            "Content": article_details["content"],
        }
    )

# Créer un DataFrame à partir des données
df = pd.DataFrame(data)
# ==================================================================================================================================================

# Etape TRANSFORM de l'ETL==========================================================================================================================


def prepare_data(df):
    df["Date"] = df["Date_Time"].map(
        lambda x: pd.to_datetime(x[:10])
    )  # Récupère la date et converti en Timestamp
    df["Year"] = df["Date_Time"].map(
        lambda x: int(x[:4])
    )  # Récupère l'année et converti en entier
    df["Month"] = df["Date_Time"].map(
        lambda x: int(x[5:7])
    )  # Récupère le mois et converti en entier
    df["Day"] = df["Date_Time"].map(
        lambda x: int(x[8:10])
    )  # Récupère le jour et converti en entier
    df["Content"] = df["Content"].map(
        lambda x: x.replace("\n", " ")
    )  # remplace les caractères \n par un espace
    df = df.drop("Date_Time", axis=1)  # supprime la colonne Date_Time
    return df


final_data = prepare_data(df)  # données néttoyées
# ===================================================================================================================================================


# Etape LOAD de l'ETL===============================================================================================================================
def load_data(host, user, password, port, data):
    # définir les paramètres pour la connexion à la base de données
    db_connection = mysql.connector.connect(
        host=host, user=user, password=password, port=port
    )
    print("connected")
    cursor = db_connection.cursor()
    create_db = (
        "CREATE DATABASE IF NOT EXISTS techcrunch;"  # création de la base de données
    )
    use_db = "USE techcrunch;"  # pointe sur la base de données
    # Création de la table
    create_query = " CREATE TABLE IF NOT EXISTS articles (id INT AUTO_INCREMENT PRIMARY KEY,category VARCHAR(255),title VARCHAR(511),link VARCHAR(255),author VARCHAR(255),content TEXT,date Date,year int,month int,day int	);"
    cursor.execute(create_db)
    cursor.execute(use_db)
    cursor.execute(create_query)
    # Charger les données dans la base de données
    for index, row in data.iterrows():
        insert_query = "INSERT INTO articles (category, title, link, author, content, date, year, month, day) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        data_tuple = (
            row["Category"],
            row["Title"],
            row["Link"],
            row["Author"],
            row["Content"],
            row["Date"],
            row["Year"],
            row["Month"],
            row["Day"],
        )
        cursor.execute(insert_query, data_tuple)

    db_connection.commit()
    cursor.close()
    db_connection.close()

    print("Données chargées dans la base de données MySQL.")


load_data("localhost", "root", "mysql_brad", "3306", final_data)
# ================================================================================================================================================

