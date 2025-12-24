from flask import Flask, render_template, request
import json, os

# from Apartment_manage.index import admin_bp

app = Flask(__name__)

# app.register_blueprint(admin_bp)
# Load JSON
def load_apartments():
    json_path = os.path.join("Data", "apartment.json")
    with open(json_path, encoding="utf-8") as a:
        return json.load(a)

with open("templates/Data/apartment.json", "r", encoding="utf-8") as f:
    apartments = json.load(f)

if __name__ == "__main__":
    app.run(debug=True)