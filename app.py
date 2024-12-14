from flask import Flask, request, jsonify, render_template
from openpyxl import Workbook, load_workbook
import os

app = Flask(__name__)

# Crear la carpeta BITS-X-FIBROSI si no existeix
SAVE_FOLDER = 'BITS-X-FIBROSI'
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Ruta per a la pàgina principal
@app.route('/')
def index():
    return render_template('app_autom.html')  # Assegura't que el fitxer HTML està a "templates"

# Ruta per gestionar la recepció de dades i guardar-les en un fitxer Excel
@app.route('/save-excel', methods=['POST'])
def save_excel():
    try:
        data = request.get_json()  # Rebre dades en format JSON
        print(f"Dades rebudes: {data}")  # Per depuració

        # Validar que les dades no estiguin buides
        if not data:
            return jsonify({'error': 'No hi ha dades per guardar.'}), 400

        # Crear o carregar el fitxer Excel
        filepath = os.path.join(SAVE_FOLDER, 'respostes_questionari.xlsx')
        if os.path.exists(filepath):
            workbook = load_workbook(filepath)
            if 'Respostes' in workbook.sheetnames:
                sheet = workbook['Respostes']
            else:
                sheet = workbook.create_sheet('Respostes')
        else:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = 'Respostes'

        # Afegir encapçalaments si la fulla està buida
        if sheet.max_row == 1 and all(cell.value is None for cell in sheet[1]):
            sheet.append(['Usuari', 'Variable 1', 'Variable 2', 'Variable 3'])

        # Afegir la nova fila amb les dades
        sheet.append([data.get('usuari'), data.get('variable1'), data.get('variable2'), data.get('variable3')])

        # Guardar el fitxer Excel
        workbook.save(filepath)
        print(f"Fitxer desat correctament a: {filepath}")

        return jsonify({'message': 'Dades guardades correctament.'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Hi ha hagut un problema en desar les dades.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
