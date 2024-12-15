from flask import Flask, request, jsonify, render_template
import openpyxl
import os

app = Flask(__name__)

# Ruta a l'arxiu Excel
EXCEL_FILE = 'form_data.xlsx'

# Definició dels capçaleres basats en les claus de formData
HEADERS = ['usuari', 'Pedigree', 'sex', 'Age at diagnosis', 'FinalDiagnosis', 'TobaccoHistory',
       'RadiologicalPattern', 'Biopsy', 'Extrapulmonary',
       'LungCancer', 'OtherCancer', 'NeoplasiaType[]',
       'HematologicAbnormalities',
       'BloodCountAbnormalities[]', 'HematologicDiseaseConfirm',
       'LiverAbnormalityBefore', 'LiverAbnormality','LiverDisease', 'LDH', 'ALT',
       'AST', 'ALP', 'GGT', 'Transaminitis', 'Cholestasis', 
       'FVC', 'DLCO',
       'FirstDegreeRelative', 'SecondDegreeRelative', 'MoreThanOneRelative',
       'GeneticMutation', 'TelomereShorteningSeverity']  

# Camps que han de ser convertits a números
NUMERIC_FIELDS = ['Pedigree', 'Age at diagnosis', 'FinalDiagnosis', 'TobaccoHistory', 'Biopsy', 'Extrapulmonary',
       'LungCancer', 'OtherCancer', 
       'HematologicAbnormalities', 'HematologicDiseaseConfirm', 'LiverAbnormalityBefore', 'LiverAbnormality', 'LDH', 'ALT',
       'AST', 'ALP', 'GGT', 'Transaminitis', 'Cholestasis', 'LiverDisease',
       'FVC', 'DLCO',
       'FirstDegreeRelative', 'SecondDegreeRelative', 'MoreThanOneRelative',
       'GeneticMutation', 'TelomereShorteningSeverity']    # Afegir altres camps si és necessari



BLOOD_COUNT_ABNORMALITIES_OPTIONS = [
    'anemia',
    'thrombocytopenia',
    'thrombocytosis',
    'lymphocytosis',
    'lymphopenia',
    'neutrophilia',
    'neutropenia',
    'leukocytosis',
    'leukopenia'
]

def initialize_excel():
    if not os.path.exists(EXCEL_FILE):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(HEADERS)
        wb.save(EXCEL_FILE)

@app.route('/')
def index():
    return render_template('app_prova.html')  # Assegura't que el teu fitxer HTML es troba en templates/index.html

@app.route('/save-excel', methods=['POST'])
def save_excel():
    data = request.get_json()

    # Validació bàsica
    if not data:
        return jsonify({'error': 'No s\'han proporcionat dades.'}), 400

    # Inicialitzar l'arxiu Excel si no existeix
    initialize_excel()

    # Carregar el llibre de treball i seleccionar la primera fulla
    wb = openpyxl.load_workbook(EXCEL_FILE)
    ws = wb.active

    # Preparar les dades de la fila basant-se en els capçaleres
    row = []
    for header in HEADERS:
        if header in BLOOD_COUNT_ABNORMALITIES_OPTIONS:
            # Assignar 1 si l'opció està seleccionada, 0 si no
            row.append(1 if header in data.get('BloodCountAbnormalities[]', []) else 0)
        else:
            value = data.get(header, '')
            if isinstance(value, list):
                value = ', '.join(value)  # Convertir llista a cadena separada per comes
            elif header in NUMERIC_FIELDS:
                try:
                    value = int(value)
                except ValueError:
                    return jsonify({'error': f'El camp {header} ha de ser un número.'}), 400
            row.append(value)

    # Afegir la fila
    ws.append(row)

    # Guardar el llibre de treball
    wb.save(EXCEL_FILE)

    # Resposta de confirmació
    return jsonify({'message': 'Dades guardades correctament!'}), 200

if __name__ == '__main__':
    app.run(debug=True)
