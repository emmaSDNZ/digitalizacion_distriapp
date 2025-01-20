import pandas as pd
import re
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Copias de los DataFrames
df_productos = pd.read_csv(" C:/Users/OPERADOR/Desktop/PROYECTO DIGITALIZACION\digitalizacion_distriapp/backend/src/notebook/L_STMaestroPrd.csv")
print(df_productos)
copy_dfProductos = df_productos.loc[:, df_productos.notna().any()].copy()  # Eliminar columnas vacías

# Este modulo estandariza los csv que provienen del proveedor.
# Función para procesar el caso de "varios productos en una fila"
def procesar_varios_productos(df):
    for column in df.columns:
        df[column] = df[column].apply(lambda x: x.split('\n') if isinstance(x, str) else ([x] if pd.notna(x) else [np.nan]))
    df_exploded_list = []
    for _, row in df.iterrows():
        row_lists = [row[col] if isinstance(row[col], list) else [row[col]] for col in df.columns]
        max_len = max(len(lst) for lst in row_lists)
        row_lists = [lst + [None] * (max_len - len(lst)) for lst in row_lists]
        exploded_row = pd.DataFrame(row_lists).T
        exploded_row.columns = df.columns
        df_exploded_list.append(exploded_row)
    return pd.concat(df_exploded_list, ignore_index=True)

# Función para procesar el caso de "un producto por fila"
def procesar_un_producto(df):
    for col in df.columns:
        df[col] = df[col].apply(lambda x: x.replace('\r\n', ' ').replace('\n', ' ') if isinstance(x, str) else x)
    return df

# Función principal para decidir el módulo a usar
def procesar_csv(file_path):
    df = pd.read_csv(file_path)
    contiene_saltos = df.iloc[:, 0].apply(lambda x: '\n' in x if isinstance(x, str) else False).any()
    if contiene_saltos:
        print("Usando el módulo: VARIOS PRODUCTOS EN UNA FILA")
        return procesar_varios_productos(df)
    else:
        print("Usando el módulo: UN PRODUCTO POR FILA")
        return procesar_un_producto(df)

# Cargar el CSV del proveedor
ruta_csv = "prueba2.csv"
df_resultado_PROVEEDOR = procesar_csv(ruta_csv)

# Función de limpieza básica de texto para la columna de descripciones
def clear_column(column):
    columna_limpia = re.sub(r'\b(\d+|mg|comp\.?|blisters?|estuche|x|ml|unidades|marca|botella|caja|referencia|cm|g|m|f\.a\.x|'
                            r'jbe\.|sol\.|env\.|lata|vial|pvo\.|sobres|gotero|cápsulas|frascos?|blister|bot\.|mcg|sp|p\.b\.)\b',
                            '', column, flags=re.IGNORECASE)
    columna_limpia = re.sub(r'\n', ' ', columna_limpia)
    columna_limpia = re.sub(r'[:\.\-,;()]', '', columna_limpia)
    columna_limpia = re.sub(r'\s+', ' ', columna_limpia).strip()
    return columna_limpia

# Limpiamos las descripciones de los productos
df_resultado_PROVEEDOR['descripcion_limpia'] = df_resultado_PROVEEDOR['DESCRIPCIÓN'].fillna('').apply(clear_column)

# Función para filtrar productos por laboratorio
def laboratorio_input_df(df, columna):
    input_name = input("Ingrese el nombre del laboratorio: ").strip()
    tablas_coincidencias = df[df[columna].str.contains(input_name, case=False, na=False)].copy()
    if not tablas_coincidencias.empty:
        print(f"Se encontraron {len(tablas_coincidencias)} productos coincidentes del laboratorio '{input_name}'.")
        tablas_coincidencias['descrip1_limpia'] = tablas_coincidencias['descrip1'].fillna('').apply(clear_column)
        return tablas_coincidencias
    else:
        print(f"No se encontraron productos del laboratorio '{input_name}'.")
        return None

column_name_laboratorio = "atrib0"
laboratorio_coincidencias_df = laboratorio_input_df(df_productos, column_name_laboratorio)

# Instanciamos el modelo de SentenceTransformer para obtener embeddings de texto
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Función para obtener embeddings de las descripciones
def get_embeddings(descriptions):
    return model.encode(descriptions.tolist())

# Comparar descripciones de productos utilizando embeddings
if laboratorio_coincidencias_df is not None:
    proveedor_embeddings = get_embeddings(df_resultado_PROVEEDOR['descripcion_limpia'])
    laboratorio_embeddings = get_embeddings(laboratorio_coincidencias_df['descrip1_limpia'])

    matches = []

    for i, prov_row in df_resultado_PROVEEDOR.iterrows():
        prov_desc = prov_row['descripcion_limpia']

        # Calculamos la similitud de coseno entre el producto proveedor y los productos del laboratorio
        cosine_similarities = cosine_similarity([proveedor_embeddings[i]], laboratorio_embeddings)

        best_match_index = cosine_similarities.argmax()  # El índice de la mejor coincidencia
        best_match_score = cosine_similarities.max()  # El puntaje de similitud

        match_info = prov_row.to_dict()
        match_info.update(laboratorio_coincidencias_df.iloc[best_match_index].to_dict())
        match_info['similaridad'] = best_match_score
        matches.append(match_info)

    df_matches = pd.DataFrame(matches)

    # Reordenamos las columnas para que la columna 'similaridad' esté al inicio
    cols = ['similaridad'] + [col for col in df_matches.columns if col != 'similaridad']
    df_matches = df_matches[cols]

    print(f"\nCoincidencias encontradas: {len(df_matches[df_matches['similaridad'] > 0])}")
    print(df_matches)

    productos_sin_coincidencia = laboratorio_coincidencias_df[~laboratorio_coincidencias_df['descrip1_limpia'].isin(
        df_matches[df_matches['similaridad'] > 0]['descrip1_limpia']
    )]

    print(f"\nProductos del laboratorio sin coincidencias: {len(productos_sin_coincidencia)}")
    print(productos_sin_coincidencia)
else:
    print("No se encontraron coincidencias para el laboratorio especificado.")
