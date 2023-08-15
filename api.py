# Importation
from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Définir les détails de connexion à la base de données
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "mysql_brad",
    "database": "techrunch",
}


# Route pour obtenir les articles en fonction de la catégorie
@app.route("/articles", methods=["GET"])
def get_articles():
    try:
        category = request.args.get(
            "category"
        )  # Récupérer la catégorie à partir des paramètres d'URL
        db_connection = mysql.connector.connect(**db_config)
        cursor = db_connection.cursor(dictionary=True)

        if category:
            query = "SELECT * FROM articles WHERE category = %s"
            cursor.execute(
                query, (category,)
            )  # Récupérer les articles de la catégorie en question
        else:
            query = "SELECT * FROM articles"
            cursor.execute(query)  # Récupérer tous les aerticles

        articles = cursor.fetchall()

        cursor.close()
        db_connection.close()

        return jsonify({"articles": articles})
    except Exception as e:
        return jsonify({"error": str(e)})


# Lancer l'application en mode debogage
if __name__ == "__main__":
    app.run(debug=True)
