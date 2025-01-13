import pandas as pd
#Funcion para convertir un archivo .xlsx a csv

# Función para convertir archivo .xlsx a .csv
def convert_xlsx_to_csv(xlsx_file_path, csv_file_path):
    # Leer el archivo Excel
    df = pd.read_excel(xlsx_file_path)

    # Guardar el archivo como CSV
    df.to_csv(csv_file_path, index=False)  # `index=False` para no guardar el índice como columna

    print(f"Archivo convertido y guardado como: {csv_file_path}")

# Ruta de entrada y salida
input_file = "/content/prueba.xlsx"  # Ruta del archivo Excel
output_file = "/content/prueba_convertido.csv"  # Ruta donde se guardará el archivo CSV

# Convertir y guardar
convert_xlsx_to_csv(input_file, output_file)

                    