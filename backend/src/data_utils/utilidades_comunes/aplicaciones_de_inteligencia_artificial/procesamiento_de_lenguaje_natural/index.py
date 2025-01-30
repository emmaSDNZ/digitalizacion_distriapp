import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from transformers import BertTokenizer, BertModel
import torch


# Configuración global
MODEL_NAME_BERT = 'dccuchile/bert-base-spanish-wwm-cased'

# Cargar el modelo BERT y el tokenizador
tokenizer = BertTokenizer.from_pretrained(MODEL_NAME_BERT)
model = BertModel.from_pretrained(MODEL_NAME_BERT)


def obtener_embedding(texto):
    """
    Obtiene el embedding de BERT para un texto dado.
    :param texto: Texto a procesar
    :return: Vector numpy con el embedding
    """
    tokens = tokenizer(texto, 
                       return_tensors='pt', 
                       padding=True, 
                       truncation=True, 
                       max_length=512)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).numpy()


def extraer_numeros(texto):
    """
    Extrae los números de una cadena de texto.
    :param texto: Texto a analizar
    :return: Lista de números encontrados
    """
    return re.findall(r'\d+', texto)


def comparar_numeros(numeros_proveedor, numeros_master):
    """
    Calcula la similitud numérica entre dos listas de números.
    :param numeros_proveedor: Lista de números del proveedor
    :param numeros_master: Lista de números del master
    :return: Coeficiente de similitud numérica
    """
    if not numeros_proveedor or not numeros_master:
        return 0  # Si alguna de las listas está vacía, no hay coincidencia
    return len(set(numeros_proveedor) & set(numeros_master)) / max(len(numeros_proveedor), len(numeros_master))


def procesar_datos(df_master, df_proveedor, descripcion_master, descripcion_proveedor):
    """
    Procesa los DataFrames y calcula la similitud de productos.
    :param df_master: DataFrame con productos master
    :param df_proveedor: DataFrame con productos de proveedores
    :param descripcion_master: Nombre de la columna de descripción en df_master
    :param descripcion_proveedor: Nombre de la columna de descripción en df_proveedor
    :return: DataFrame con resultados de similitud
    """
    df_master['numeros'] = df_master[descripcion_master].apply(extraer_numeros)
    df_proveedor['numeros'] = df_proveedor[descripcion_proveedor].apply(extraer_numeros)
    df_master['embedding_Master'] = df_master[descripcion_master].apply(obtener_embedding)

    resultados = []
    for _, row in tqdm(df_proveedor.iterrows(), total=len(df_proveedor)):
        emb_proveedor = obtener_embedding(row[descripcion_proveedor])
        numeros_proveedor = row['numeros']
        
        similitudes = [
            (row_master[descripcion_master], calcular_similitud_final(
                emb_proveedor, row_master['embedding_Master'],
                numeros_proveedor, row_master['numeros']
            )) for _, row_master in df_master.iterrows()
        ]
        
        top_3_matches = sorted(similitudes, key=lambda x: x[1], reverse=True)[:3]
        
        for match, similitud in top_3_matches:
            resultados.append({
                'descripcion_proveedor': row[descripcion_proveedor],
                'descripcion_match': match,
                'similitud': similitud,
            })
    
    return pd.DataFrame(resultados)
###
#
#
#
#
# Función para cargar modelos BERT


import pandas as pd
import re
import numpy as np
from tqdm import tqdm
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, AutoModel
import torch


def cargar_modelo(modelo_nombre):
    tokenizer = AutoTokenizer.from_pretrained(modelo_nombre)
    model = AutoModel.from_pretrained(modelo_nombre)
    return tokenizer, model


# Función para obtener embeddings de un modelo dado
def obtener_embedding(texto, tokenizer, model):
    tokens = tokenizer(texto, return_tensors='pt', padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        output = model(**tokens)
    return output.last_hidden_state.mean(dim=1).numpy()

# Función para extraer números
def extraer_numeros(texto):
    return re.findall(r'\d+', texto)


# Función para comparar números
def comparar_numeros(numeros_proveedor, numeros_master):
    if not numeros_proveedor or not numeros_master:
        return 0  
    return len(set(numeros_proveedor) & set(numeros_master)) / max(len(numeros_proveedor), len(numeros_master))

# Función para calcular la similitud combinada
def calcular_similitud_final(emb_proveedor, emb_master, numeros_proveedor, numeros_master):
    similitud_textual = cosine_similarity(emb_proveedor, emb_master)[0][0]
    similitud_numerica = comparar_numeros(numeros_proveedor, numeros_master)
    return 0.8 * similitud_textual + 0.2 * similitud_numerica  


# Función principal para comparar productos y generar resultados
def procesar_comparacion(df_master, df_proveedor, modelo_nombre, nombre_modelo, columna_master, columna_proveedor):
    tokenizer, model = cargar_modelo(modelo_nombre)

    # Normalización y extracción de números
    df_master['numeros'] = df_master[columna_master].apply(extraer_numeros)
    df_proveedor['numeros'] = df_proveedor[columna_proveedor].apply(extraer_numeros)

    # Obtener embeddings del master
    df_master['embedding_Master'] = df_master[columna_master].apply(
        lambda x: obtener_embedding(x, tokenizer, model)
    )

    # Generación de resultados en formato vertical
    resultados_vertical = []
    for idx, row in tqdm(df_proveedor.iterrows(), total=len(df_proveedor)):
        emb_proveedor = obtener_embedding(row[columna_proveedor], tokenizer, model)
        numeros_proveedor = row['numeros']

        similitudes = []
        for idx_master, row_master in df_master.iterrows():
            emb_master = row_master['embedding_Master']
            numeros_master = row_master['numeros']

            similitud_final = calcular_similitud_final(emb_proveedor, emb_master, numeros_proveedor, numeros_master)
            similitudes.append((row_master[columna_master], similitud_final))

        # Obtener los 3 mejores resultados
        top_3_matches = sorted(similitudes, key=lambda x: x[1], reverse=True)[:3]

        # Agregar coincidencias en formato vertical
        for match, similitud in top_3_matches:
            resultados_vertical.append({
                'descripcion_proveedor': row[columna_proveedor],
                'descripcion_match': match,
                'similitud': similitud,
            })

    # Guardar los resultados con el nombre del modelo
    nombre_archivo = f"resultados_{nombre_modelo}.csv"
    df_resultados_vertical = pd.DataFrame(resultados_vertical)
    df_resultados_vertical.to_csv(nombre_archivo, index=False)

    print(f"Proceso completado. Resultados guardados en '{nombre_archivo}'")
