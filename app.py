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
model = load('model_logistic_regression_progression.pkl')
print("Model carregat correctament.")

codificacions = {
    'variable2': {
        'option1': 1,
        'option2': 2,
        'option3': 0
    },
    'variable1': {
        'yes': 1,
        'no': 0
    }
}

# Ruta per a la pàgina principal
@app.route('/')
def index():
    return render_template('app_autom.html')  # Assegura't que aquest fitxer HTML està a /templates

# Ruta per guardar les dades al fitxer Excel
@app.route('/save-excel', methods=['POST'])
def save_excel():
    try:
        data = request.get_json()  # Rebre dades en format JSON
        print(f"Dades rebudes: {data}")  # Per depuració

        if not data:
            return jsonify({'error': 'No hi ha dades per guardar.'}), 400
        
        # Codifica les variables
        data['variable1'] = codificacions['variable1'].get(data.get('variable1'), -1)  # Valors no definits es codifiquen com -1
        data['variable2'] = codificacions['variable2'].get(data.get('variable2'), -1)

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
            sheet.append(['Usuari', 'Variable 1', 'Variable 2', 'Variable 3', 'Predicció'])

        # Afegir la nova fila amb les dades i la predicció
        variables = ['variable1', 'variable2', 'variable3']
        user_input = [data.get(var) for var in ['usuari'] + variables]

        # Preprocessar les dades noves per predicció
        df_input = pd.DataFrame([data], columns=['variable1', 'variable2', 'variable3'])
        df_input = pd.get_dummies(df_input, drop_first=True)

        # Afegir columnes que falten i reordenar-les
        model_columns = [col for col in sheet[1] if col.value not in ['Usuari', 'Predicció']]
        for col in model_columns:
            if col not in df_input.columns:
                df_input[col] = 0
        df_input = df_input[model_columns]

        prediction = model.predict(df_input)[0]
        user_input.append(prediction)

        sheet.append(user_input)

        # Guardar l'Excel
        workbook.save(filepath)

        return jsonify({'message': 'Dades guardades correctament i predicció feta.', 'predicció': int(prediction)}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Hi ha hagut un problema en desar les dades o fer la predicció.'}), 500


if __name__ == '__main__':
    app.run(debug=True)
