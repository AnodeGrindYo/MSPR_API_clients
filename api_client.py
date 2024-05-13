import os
from flask import Flask, request, jsonify, make_response
import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()

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

@app.route('/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clients")
    customers = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(customers)

@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clients WHERE ClientID = %s", (id,))
    customer = cursor.fetchone()
    cursor.close()
    conn.close()
    if customer:
        return jsonify(customer)
    else:
        return make_response(jsonify({"error": "Customer not found"}), 404)

@app.route('/customers', methods=['POST'])
def create_customer():
    if not request.json or not 'email' in request.json:
        return make_response(jsonify({"error": "Bad request"}), 400)
    customer = {
        'Nom': request.json.get('Nom', ""),
        'Prenom': request.json.get('Prenom', ""),
        'Email': request.json['email'],
        'Telephone': request.json.get('Telephone', ""),
        'Adresse': request.json.get('Adresse', ""),
        'Ville': request.json.get('Ville', ""),
        'CodePostal': request.json.get('CodePostal', ""),
        'Pays': request.json.get('Pays', "")
    }
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Clients (Nom, Prenom, Email, Telephone, Adresse, Ville, CodePostal, Pays) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                   (customer['Nom'], customer['Prenom'], customer['Email'], customer['Telephone'], customer['Adresse'], customer['Ville'], customer['CodePostal'], customer['Pays']))
    conn.commit()
    cursor.close()
    conn.close()
    return make_response(jsonify(customer), 201)

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Clients WHERE ClientID = %s", (id,))
    customer = cursor.fetchone()
    if not customer:
        return make_response(jsonify({"error": "Customer not found"}), 404)
    data = request.json
    updates = []
    for field in ['Nom', 'Prenom', 'Email', 'Telephone', 'Adresse', 'Ville', 'CodePostal', 'Pays']:
        if field in data:
            updates.append(f"{field} = %s")
    update_query = "UPDATE Clients SET " + ", ".join(updates) + " WHERE ClientID = %s"
    cursor.execute(update_query, [data[field] for field in data if field in updates] + [id])
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": "Customer updated"})

@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Clients WHERE ClientID = %s", (id,))
    conn.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    conn.close()
    if affected_rows:
        return jsonify({"success": "Customer deleted"})
    else:
        return make_response(jsonify({"error": "Customer not found"}), 404)

if __name__ == '__main__':
    app.run(debug=True)

