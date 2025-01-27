import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def vectorizar_descripciones(df_master, df_proveedor):
    """
    Vectoriza las descripciones de productos de los DataFrames master y proveedor.
    Devuelve la matriz de similitud de coseno entre los productos de ambos DataFrames.
    """
    # Concatenar las descripciones de los productos
    descripciones_completas = df_master['descripcion_limpia_producto'].tolist() + df_proveedor['descripcion_limpia_proveedor'].tolist()
    
    # Vectorizar las descripciones usando TfidfVectorizer
    vectorizer = TfidfVectorizer().fit_transform(descripciones_completas)
    
    # Calcular la similitud de coseno entre las descripciones de la master y del proveedor
    cos_sim_matrix = cosine_similarity(vectorizer[:len(df_master)], vectorizer[len(df_master):])
    
    return cos_sim_matrix

def obtener_mejores_coincidencias(df_master, df_proveedor, cos_sim_matrix):
    """
    Encuentra la mejor coincidencia de similitud entre los productos del proveedor y los productos de la master.
    Devuelve una lista de diccionarios con la información de los productos y su similitud.
    """
    matches = []
    
    for i, prov_row in df_proveedor.iterrows():
        prov_info = prov_row.to_dict()  # Información completa del producto del proveedor
        
        # Obtener las similitudes entre el producto del proveedor y todos los productos de la master
        if i < cos_sim_matrix.shape[1]:  # Asegurarse de que i no exceda el número de columnas
            similitudes = cos_sim_matrix[:, i]  # Similitudes entre el proveedor i y todos los productos de la master
            
            # Encontrar la mejor coincidencia (la mayor similitud)
            max_similitud = np.max(similitudes)  # La mayor similitud encontrada
            best_match_index = np.argmax(similitudes)  # Índice del producto de la master con la mayor similitud
            
            # Recuperar la fila de la master correspondiente a la mejor coincidencia
            best_match_info = df_master.iloc[best_match_index].to_dict()
            
            # Unir la información del proveedor y la mejor coincidencia
            best_match_info.update(prov_info)
            best_match_info['similaridad'] = max_similitud  # Añadir la similitud más alta
            
            matches.append(best_match_info)  # Añadir la coincidencia a la lista
    
    return matches

def crear_dataframe_matches(df_Proveedor, matches):
    """
    Crea un DataFrame con las coincidencias encontradas entre los productos del proveedor y los productos de la master.
    """
    # Convertir la lista de matches a un DataFrame
    df_matches = pd.DataFrame(matches)

    # Si deseas mantener todas las filas del proveedor, incluyendo aquellas sin coincidencias, puedes hacer un merge
    df_matches_all = pd.merge(df_Proveedor, df_matches, how='left', on='descripcion_limpia_proveedor')

    # Reordenar columnas para que 'similaridad' esté al principio
    cols = ['similaridad'] + [col for col in df_matches_all.columns if col != 'similaridad']
    df_matches_all = df_matches_all[cols]
    
    return df_matches_all

# Función principal para ejecutar el proceso
def main_principal(df_MasterProductos_Filtro, df_Proveedor):
    # Paso 1: Vectorizar descripciones
    cos_sim_matrix = vectorizar_descripciones(df_MasterProductos_Filtro, df_Proveedor)
    
    # Paso 2: Obtener las mejores coincidencias
    matches = obtener_mejores_coincidencias(df_MasterProductos_Filtro, df_Proveedor, cos_sim_matrix)
    
    # Paso 3: Crear DataFrame con los resultados
    df_matches_all = crear_dataframe_matches(df_Proveedor, matches)
    
    # Mostrar el resultado
    return df_matches_all

