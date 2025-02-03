import pandas as pd  # Importación de pandas para manipulación de datos
import re  # Importación de expresiones regulares para extracción de números
import numpy as np  # Importación de numpy para manejo de arrays numéricos
from tqdm import tqdm  # Importación de tqdm para barras de progreso
from sklearn.metrics.pairwise import cosine_similarity  # Importación de la función para calcular la similitud coseno
from transformers import AutoTokenizer, AutoModel  # Importación de herramientas de Hugging Face para modelos de lenguaje
import torch  # Importación de PyTorch para el procesamiento de modelos de aprendizaje automático

# Función para cargar el modelo y el tokenizer
def cargar_modelo(modelo_nombre):
    """
    Carga el modelo de lenguaje y el tokenizer desde Hugging Face utilizando el nombre del modelo.
    
    Args:
        modelo_nombre (str): Nombre del modelo a cargar desde Hugging Face.
        
    Returns:
        tokenizer (transformers.tokenization_utils.BaseTokenizer): Tokenizer para el modelo.
        model (transformers.modeling_utils.PreTrainedModel): Modelo preentrenado cargado.
    """
    tokenizer = AutoTokenizer.from_pretrained(modelo_nombre)  # Carga el tokenizer para tokenizar los textos
    model = AutoModel.from_pretrained(modelo_nombre)  # Carga el modelo preentrenado
    return tokenizer, model  # Retorna ambos objetos

# Función para obtener el embedding de un texto utilizando el modelo y tokenizer
def obtener_embedding(texto, tokenizer, model):
    """
    Obtiene el embedding de un texto dado utilizando un modelo de lenguaje preentrenado.
    
    Args:
        texto (str): Texto de entrada para el cual se genera el embedding.
        tokenizer (transformers.tokenization_utils.BaseTokenizer): Tokenizer utilizado para tokenizar el texto.
        model (transformers.modeling_utils.PreTrainedModel): Modelo preentrenado utilizado para obtener el embedding.
        
    Returns:
        numpy.ndarray: Embedding de texto generado por el modelo.
    """
    tokens = tokenizer(texto, return_tensors='pt', padding=True, truncation=True, max_length=512)  # Tokeniza el texto
    with torch.no_grad():  # Desactiva el cálculo del gradiente para optimizar el proceso
        output = model(**tokens)  # Pasa los tokens por el modelo para obtener la representación
    return output.last_hidden_state.mean(dim=1).numpy()  # Retorna el embedding promedio de la última capa

# Función para calcular la similitud combinada entre el texto y los números
def calcular_similitud_final(emb_proveedor, emb_master, numeros_proveedor, numeros_master):
    """
    Calcula la similitud combinada entre la similitud textual y la similitud numérica.
    
    Args:
        emb_proveedor (numpy.ndarray): Embedding del texto del proveedor.
        emb_master (numpy.ndarray): Embedding del texto del master.
        numeros_proveedor (list): Números extraídos de la descripción del proveedor.
        numeros_master (list): Números extraídos de la descripción del master.
        
    Returns:
        float: Similitud combinada entre el texto y los números.
    """
    similitud_textual = cosine_similarity(emb_proveedor, emb_master)[0][0]  # Similitud coseno entre los embeddings
    similitud_numerica = comparar_numeros(numeros_proveedor, numeros_master)  # Similitud numérica
    return 0.8 * similitud_textual + 0.2 * similitud_numerica  # Peso de la similitud textual y numérica


# Función para extraer números de un texto
def extraer_numeros(texto):
    """
    Extrae los números de un texto utilizando expresiones regulares.
    
    Args:
        texto (str): Texto del cual se extraen los números.
        
    Returns:
        list: Lista de cadenas con los números extraídos del texto.
    """
    return re.findall(r'\d+', texto)  # Encuentra todas las secuencias de dígitos en el texto

# Función para comparar los números entre el proveedor y el master

def comparar_numeros(numeros_proveedor, numeros_master):
    """
    Compara los números entre las descripciones de un proveedor y el master.
    
    Args:
        numeros_proveedor (list): Lista de números extraídos de la descripción del proveedor.
        numeros_master (list): Lista de números extraídos de la descripción del master.
        
    Returns:
        float: Proporción de coincidencia entre los números de ambas listas.
    """
    if not numeros_proveedor or not numeros_master:
        return 0  # Si alguna lista está vacía, no hay coincidencia
    return len(set(numeros_proveedor) & set(numeros_master)) / max(len(numeros_proveedor), len(numeros_master))  # Proporción de coincidencias



# Función principal para comparar productos y generar resultados con las tres mejores coincidencias
def procesar_comparacion_texto(df_master, df_proveedor, modelo_nombre, nombre_modelo, columna_descripcion_master, columna_descripcion_proveedor): 
    """
    Procesa la comparación de descripciones entre el DataFrame maestro y el DataFrame del proveedor
    utilizando embeddings generados por un modelo NLP y análisis de similitud numérica.
    
    Args:
        df_master (pd.DataFrame): DataFrame maestro con las descripciones de referencia.
        df_proveedor (pd.DataFrame): DataFrame del proveedor con las descripciones a comparar.
        modelo_nombre (str): Nombre del modelo NLP a utilizar.
        nombre_modelo (str): Nombre descriptivo del modelo.
        columna_descripcion_master (str): Nombre de la columna con las descripciones en df_master.
        columna_descripcion_proveedor (str): Nombre de la columna con las descripciones en df_proveedor.
    
    Returns:
        pd.DataFrame: DataFrame del proveedor con las mejores coincidencias y similitudes agregadas.
    """
    tokenizer, model = cargar_modelo(modelo_nombre)  # Carga el modelo y el tokenizer

    # Normalización y extracción de números desde las descripciones
    df_master['numeros'] = df_master[columna_descripcion_master].apply(extraer_numeros)  # Extrae números del master
    df_proveedor['numeros'] = df_proveedor[columna_descripcion_proveedor].apply(extraer_numeros)  # Extrae números del proveedor

    # Obtener embeddings de las descripciones en el DataFrame maestro
    df_master['embedding_Master'] = df_master[columna_descripcion_master].apply(
        lambda x: obtener_embedding(x, tokenizer, model)  # Convierte cada descripción en un vector numérico
    )

    # Lista para almacenar los mejores resultados de coincidencia
    mejores_matches = []  

    for idx, row in tqdm(df_proveedor.iterrows(), total=len(df_proveedor)):  # Itera sobre cada fila del proveedor
        emb_proveedor = obtener_embedding(row[columna_descripcion_proveedor], tokenizer, model)  # Obtiene el embedding del proveedor
        numeros_proveedor = row['numeros']  # Obtiene los números extraídos del proveedor

        similitudes = []  # Lista para almacenar las similitudes con el maestro
        for idx_master, row_master in df_master.iterrows():  # Itera sobre cada fila del DataFrame maestro
            emb_master = row_master['embedding_Master']  # Obtiene el embedding del master
            numeros_master = row_master['numeros']  # Obtiene los números extraídos del master

            # Calcula la similitud combinada entre la descripción del proveedor y la del maestro
            similitud_final = calcular_similitud_final(emb_proveedor, emb_master, numeros_proveedor, numeros_master)  
            
            # Agrega los resultados de similitud a la lista
            similitudes.append((row_master[columna_descripcion_master], similitud_final, row_master.name, row_master['niprod'], row_master['descripcion_limpia_producto']))

        # Obtener las 3 mejores coincidencias ordenadas por mayor similitud
        top_3_matches = sorted(similitudes, key=lambda x: x[1], reverse=True)[:3]  

        # Agregar las coincidencias a la lista de mejores matches
        for match, similitud, idx_producto, niprod, descripcion_limpia_producto in top_3_matches:
            mejores_matches.append({
                'index_proveedor': row.name,  # Índice del producto en el proveedor
                'descripcion_proveedor': row[columna_descripcion_proveedor],  # Descripción original del proveedor
                'descripcion_match': match,  # Descripción del producto en el master con mayor similitud
                'similitud': similitud,  # Valor de similitud calculado
                'niprod': niprod,  # Identificador único del producto en el master
                'descripcion_limpia_producto': descripcion_limpia_producto  # Descripción procesada del producto
            })

    # Convertir los mejores matches en un DataFrame
    df_mejores_matches = pd.DataFrame(mejores_matches)

    # Fusionar los resultados con el DataFrame del proveedor para agregar la información de las coincidencias
    df_proveedor = df_proveedor.merge(
        df_mejores_matches[['index_proveedor', 'niprod', 'descripcion_limpia_producto', 'similitud']], 
        left_index=True, 
        right_on='index_proveedor', 
        how='left'
    )

    return df_proveedor  # Retorna el DataFrame del proveedor con la información de coincidencias agregada
