import pandas as pd

# Función para convertir archivo .xlsx a .csv   
def convert_xlsx_to_csv(xlsx_file_path, csv_file_path):
    # Leer el archivo Excel
    df = pd.read_excel(xlsx_file_path)

    # Guardar el archivo como CSV
    df.to_csv(csv_file_path, index=False)  # `index=False` para no guardar el índice como columna

    print(f"Archivo convertido y guardado como: {csv_file_path}")