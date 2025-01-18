from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    reorder_level = db.Column(db.Integer, nullable=False)

# Initialize Database
def initialize_database():
    with app.app_context():
        db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    inventory = Inventory.query.all()
    return jsonify([{
        "id": item.id,
        "product": item.product,
        "location": item.location,
        "stock": item.stock,
        "reorder_level": item.reorder_level
    } for item in inventory])

@app.route('/api/update_stock', methods=['POST'])
def update_stock():
    data = request.json
    product_id = data.get('id')
    new_stock = data.get('stock')

    item = Inventory.query.get(product_id)
    if item:
        item.stock = new_stock
        db.session.commit()
        return jsonify({"message": f"Stock for {item.product} updated to {new_stock} units."}), 200

    return jsonify({"error": "Product not found"}), 404

@app.route('/api/forecast', methods=['POST'])
def forecast():
    data = request.json
    product_id = data.get('id')
    item = Inventory.query.get(product_id)

    if not item:
        return jsonify({"error": "Product not found"}), 404

    historical_sales = np.array([100, 120, 150, 130, 170]).reshape(-1, 1)
    periods = np.array([1, 2, 3, 4, 5]).reshape(-1, 1)

    model = LinearRegression()
    model.fit(periods, historical_sales)

    future_periods = np.array([6, 7, 8, 9, 10]).reshape(-1, 1)
    forecast = model.predict(future_periods).flatten().tolist()

    return jsonify({
        "product": item.product,
        "forecast": forecast
    })

@app.route('/api/alerts', methods=['GET'])
def alerts():
    inventory = Inventory.query.all()
    alerts = []

    for item in inventory:
        if item.stock < item.reorder_level:
            alerts.append({
                "product": item.product,
                "location": item.location,
                "stock": item.stock,
                "reorder_level": item.reorder_level,
                "alert": "Low Stock"
            })
        elif item.stock > item.reorder_level * 2:
            alerts.append({
                "product": item.product,
                "location": item.location,
                "stock": item.stock,
                "reorder_level": item.reorder_level,
                "alert": "Overstock"
            })

    return jsonify(alerts)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
