from flask import Flask, render_template, request, jsonify
import os
import openpyxl

app = Flask(__name__)

# Ruta principal para cargar la página HTML
@app.route('/')
def index():
    return render_template('app_autom.html')  # Asegúrate de que el archivo HTML esté en la carpeta "templates"

# Ruta para guardar los datos
@app.route('/save-excel', methods=['POST'])
def save_excel():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data received'}), 400

    # Guardar datos en Excel
    filename = 'respostes_questionari.xlsx'
    if not os.path.exists(filename):
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['Usuari', 'Variable1', 'Variable2', 'Variable3'])  # Encabezados
        workbook.save(filename)

    workbook = openpyxl.load_workbook(filename)
    sheet = workbook.active
    for row in data:
        sheet.append([row.get('usuari'), row.get('variable1'), row.get('variable2'), row.get('variable3')])
    workbook.save(filename)

    return jsonify({'status': 'success', 'message': 'Data saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)
