import os
from flask import Flask, request, jsonify, make_response
import pymysql
import pymysql.cursors

app = Flask(__name__)

# Configuration de la connexion à la base de données
db_config = {
    'host': os.getenv('DB_HOST'),
    'port': 3306,
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'db': os.getenv('DB_NAME'),
    'charset': os.getenv('DB_CHARSET'),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    connection = pymysql.connect(**db_config)
    return connection

@app.route('/produits', methods=['GET'])
def get_produits():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits")
    produits = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(produits)

@app.route('/produits/<int:id>', methods=['GET'])
def get_produit(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits WHERE ProduitID = %s", (id,))
    produit = cursor.fetchone()
    cursor.close()
    conn.close()
    if produit:
        return jsonify(produit)
    else:
        return make_response(jsonify({"error": "Produit not found"}), 404)

@app.route('/produits', methods=['POST'])
def create_produit():
    if not request.json or not 'Nom' in request.json or not 'Prix' in request.json or not 'Stock' in request.json:
        return make_response(jsonify({"error": "Bad request"}), 400)
    produit = {
        'Nom': request.json['Nom'],
        'Description': request.json.get('Description', ""),
        'Prix': request.json['Prix'],
        'Stock': request.json['Stock'],
        'Categorie': request.json.get('Categorie', "")
    }
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produits (Nom, Description, Prix, Stock, Categorie) VALUES (%s, %s, %s, %s, %s)",
                   (produit['Nom'], produit['Description'], produit['Prix'], produit['Stock'], produit['Categorie']))
    conn.commit()
    cursor.close()
    conn.close()
    return make_response(jsonify(produit), 201)

@app.route('/produits/<int:id>', methods=['PUT'])
def update_produit(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produits WHERE ProduitID = %s", (id,))
    produit = cursor.fetchone()
    if not produit:
        return make_response(jsonify({"error": "Produit not found"}), 404)
    data = request.json
    updates = []
    for field in ['Nom', 'Description', 'Prix', 'Stock', 'Categorie']:
        if field in data:
            updates.append(f"{field} = %s")
    update_query = "UPDATE produits SET " + ", ".join(updates) + " WHERE ProduitID = %s"
    cursor.execute(update_query, [data[field] for field in data if field in updates] + [id])
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": "Produit updated"})

@app.route('/produits/<int:id>', methods=['DELETE'])
def delete_produit(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produits WHERE ProduitID = %s", (id,))
    conn.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    conn.close()
    if affected_rows:
        return jsonify({"success": "Produit deleted"})
    else:
        return make_response(jsonify({"error": "Produit not found"}), 404)

if __name__ == '__main__':
    app.run(debug=True)
