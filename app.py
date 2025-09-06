'''
1. Időadat

    Hónap / dátum (pl. 2025-01, 2025-02…)

2. Értékadatok (attól függően, mit elemzel):

    Bevétel (pl. fizetés, hozam, nyereség)

    Kiadás (pl. költségek, veszteség)

    Megtakarítás / egyenleg

    Portfólió aktuális értéke (ha befektetéseket követsz)

3. Opcionális adatok:

    Befektetési típus (részvény, kripto, kötvény, stb.)

    Kategória (pl. fix kiadás, extra bevétel, stb.)

    Jegyzet / megjegyzés
'''
from flask import Flask, render_template, request, url_for
import os
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

def read_file(path):
    """Név: szám párokat olvas be"""
    labels, values = [], []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines:
        if ":" in line:
            name, val = line.split(":")
            labels.append(name.strip())
            try:
                values.append(float(val.strip()))
            except ValueError:
                values.append(0)
    return labels, values, "".join(lines)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    if "portfolio_file" not in request.files:
        return "Nincs fájl kiválasztva!", 400
    
    file = request.files["portfolio_file"]
    if file.filename == "":
        return "Üres fájlnév!", 400
    
    # egyedi fájlnév dátummal
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_filename = f"{timestamp}_{file.filename}"
    save_path = os.path.join(UPLOAD_DIR, save_filename)
    file.save(save_path)
    
    # jelenlegi fájl tartalom
    labels, values, content = read_file(save_path)
    
    # előző fájl keresése (ha van)
    uploaded_files = sorted(os.listdir(UPLOAD_DIR))
    prev_labels, prev_values = [], []
    if len(uploaded_files) > 1:
        prev_file = os.path.join(UPLOAD_DIR, uploaded_files[-2])
        prev_labels, prev_values, _ = read_file(prev_file)
    
    # diagram készítése
    plt.figure(figsize=(10, 6))
    x = range(len(labels))
    
    if prev_values:  # ha van előző adatsor
        width = 0.35
        plt.bar([i - width/2 for i in x], prev_values, width=width, label="Előző hónap", color="lightgray")
        plt.bar([i + width/2 for i in x], values, width=width, label="Aktuális hónap", color="skyblue")
        plt.legend()
    else:
        plt.bar(x, values, color="skyblue")
    
    plt.xticks(x, labels, rotation=45, ha="right")
    plt.title("Adatok összehasonlítása" if prev_values else "Aktuális adatok")
    plt.tight_layout()
    
    chart_path = os.path.join(STATIC_DIR, "chart.png")
    plt.savefig(chart_path)
    plt.close()
    
    return render_template(
        "result.html",
        filename=file.filename,
        content=content,
        chart_url=url_for("static", filename="chart.png"),
        has_prev=bool(prev_values)
    )

if __name__ == "__main__":
    app.run(debug=True)
