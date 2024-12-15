from flask import Flask, request, jsonify, render_template
from openpyxl import Workbook, load_workbook
from joblib import load
import pandas as pd
import os

app = Flask(__name__)

# Crear la carpeta de dades
SAVE_FOLDER = 'BITS-X-FIBROSI'
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)

# Carregar el model entrenat
model = load('model_death.pkl')
print("Model carregat correctament.")

# Ruta per a la pàgina principal
@app.route('/')
def index():
    return render_template('app_prova.html')  # Assegura't que aquest fitxer HTML està a /templates

# Ruta per guardar les dades al fitxer Excel
@app.route('/save-excel', methods=['POST'])
def save_excel():
    try:
        data = request.get_json()  # Rebre dades en format JSON
        print(f"Dades rebudes: {data}")  # Per depuració

        if not data:
            return jsonify({'error': 'No hi ha dades per guardar.'}), 400

        # Convert lists to strings
        data['NeoplasiaType'] = ', '.join(data.get('NeoplasiaType', []))
        data['BloodCountAbnormalities'] = ', '.join(data.get('BloodCountAbnormalities', []))
        data['HematologicDiseaseTypes'] = ', '.join(data.get('HematologicDiseaseTypes', []))
        data['MutationType'] = ', '.join(data.get('MutationType', []))

        # Crear o carregar el fitxer Excel
        filepath = os.path.join(SAVE_FOLDER, 'respostes_questionari.xlsx')
        if os.path.exists(filepath):
            workbook = load_workbook(filepath)
        else:
            workbook = Workbook()

        # Obtenir o crear la fulla de respostes
        sheet_name = 'Respostes'
        if sheet_name in workbook.sheetnames:
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.create_sheet(sheet_name)

        # Afegir els encapçalaments si no existeixen
        if sheet.max_row == 1 and all(cell.value is None for cell in sheet[1]):
            sheet.append(list(data.keys()) + ['Predicció'])

        # Afegir la nova fila amb les dades
        sheet.append(list(data.values()))

        # Guardar l'Excel
        workbook.save(filepath)

        # Convertir les dades a un DataFrame
        df_input = pd.DataFrame([data])

        # Aplicar One-Hot Encoding
        df_input = pd.get_dummies(df_input, drop_first=True)

        # Ensure all columns expected by the model are present
        model_columns = model.feature_names_in_
        missing_cols = set(model_columns) - set(df_input.columns)
        for col in missing_cols:
            df_input[col] = 0  # Add missing columns with default value 0

        df_input = df_input[model_columns]  # Reorder columns to match the model

        # Preprocessar les dades noves per predicció
        prediction = model.predict(df_input)[0]
        print(f"Predicció: {prediction}")  # Per depuració

        # Afegir la predicció a la fila corresponent al fitxer Excel
        sheet.cell(row=sheet.max_row, column=len(data) + 1).value = prediction
        workbook.save(filepath)

        return jsonify({'message': 'Dades guardades correctament i predicció feta.', 'predicció': int(prediction)}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Hi ha hagut un problema en desar les dades o fer la predicció.'}), 500


if __name__ == '__main__':
    app.run(debug=True)