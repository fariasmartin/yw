from pathlib import Path
import json
from string import Template
import pandas as pd  # (opcional) puedes eliminarlo si no lo usas

# === CAMBIO: Template con delimitador '§' ===
class CTemplate(Template):
    delimiter = '§'   # usamos § en vez de $

# Load JSON data
with open("data/centers.json", "r", encoding="utf-8") as f:
    centers = json.load(f)

with open("data/professors.json", "r", encoding="utf-8") as f:
    professors = json.load(f)

# === CAMBIO: cargar plantillas con CTemplate ===
with open("generate_professors_and_centers_files/center_template.qmd", "r", encoding="utf-8") as f:
    center_template = CTemplate(f.read())

with open("generate_professors_and_centers_files/professor_template.qmd", "r", encoding="utf-8") as f:
    professor_template = CTemplate(f.read())

# Ensure output directories exist
Path("centers").mkdir(exist_ok=True)
Path("professors").mkdir(exist_ok=True)

def clean_filename(text):
    return (text.lower().replace(" ", "-")
            .replace("á", "a").replace("é", "e")
            .replace("í", "i").replace("ó", "o")
            .replace("ú", "u").replace("ñ", "n"))

# Generate professor QMD files
for professor in professors:
    filename = f"professors/{clean_filename(professor['id'])}.qmd"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(professor_template.substitute(title=professor["name"], id=professor["id"]))

# Generate center QMD files
for center in centers:
    filename = f"centers/{clean_filename(center['id'])}.qmd"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(center_template.substitute(title=center["name"], id=center["id"]))
