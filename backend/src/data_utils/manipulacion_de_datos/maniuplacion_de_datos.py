import re
import pandas as pd


def cargar_datos(ruta_csv):
    """
    Carga un DataFrame desde un archivo CSV y reemplaza valores no válidos.

    Parámetros:
        ruta_csv (str): Ruta del archivo CSV a cargar.

    Retorna:
        pd.DataFrame: DataFrame con los datos cargados y limpiados.
    """
    # Cargar el CSV
    df = pd.read_csv(ruta_csv)
    
    # Reemplazar valores inválidos (NaN, inf, -inf)
    df.replace([float('inf'), float('-inf')], None, inplace=True)      
    return df


def remover_filas_columnas_nulas(df):
    """
    Elimina filas y columnas completamente vacías en el DataFrame.

    Parámetros:
        df (pd.DataFrame): DataFrame a limpiar.

    Retorna:
        pd.DataFrame: DataFrame limpio, sin filas ni columnas vacías.
    """
    df = df.dropna(how='all')  # Elimina filas completamente vacías
    df = df.dropna(axis=1, how='all')  # Elimina columnas completamente vacías
    return df.copy()


def generar_descripcion(df, col1, col2, col_destino):
    """
    Genera una nueva columna de descripción combinando dos columnas de texto.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos.
        col1 (str): Nombre de la primera columna a combinar.
        col2 (str): Nombre de la segunda columna a combinar.
        col_destino (str): Nombre de la columna donde se guardará la descripción combinada.

    Retorna:
        pd.DataFrame: DataFrame con la nueva columna de descripción.
    """
    df[col_destino] = df[col1].fillna('') + " " + df[col2].fillna('')
    return df


def procesar_descripcion(df, col):
    """
    Aplica procesamiento a la columna de descripción del DataFrame.

    Este procesamiento puede incluir técnicas de NLP, normalización, eliminación de caracteres especiales, etc.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos.
        col (str): Nombre de la columna de descripción a procesar.

    Retorna:
        pd.DataFrame: DataFrame con la descripción procesada.
    """
    return procesar_descripcion(df, col)  # Se asume que la función procesar_descripcion() ya está implementada


def estandarizado_columnas(df, col_1, col_2, descripcion_limpia):
    """
    Combina columnas específicas de un DataFrame en una nueva columna, si existen.
    Convierte las columnas del DataFrame a minúsculas antes de realizar las validaciones.

    Parámetros:
        df (pd.DataFrame): El DataFrame del proveedor.
        col_1 (str): Nombre de la primera columna a combinar.
        col_2 (str): Nombre de la segunda columna a combinar.
        descripcion_limpia_proveedor (str): Nombre de la nueva columna resultante.

    Retorna:
        pd.DataFrame: El DataFrame actualizado con la nueva columna o un mensaje de error.
    """
    # Convertir las columnas del DataFrame a minúsculas
    df.columns = df.columns.str.lower()

    # Convertir los nombres de las columnas a minúsculas para garantizar coincidencias
    col_1 = col_1.lower()
    col_2 = col_2.lower()

    # Validar si las columnas existen y combinar datos
    if col_1 in df.columns and col_2 in df.columns:
        # Ambas columnas existen
        df[descripcion_limpia] = (
            df[col_1].fillna('') + ' ' + df[col_2].fillna('')
        ).str.strip()
    elif col_1 in df.columns:
        # Solo existe col_1
        df[descripcion_limpia] = df[col_1].fillna('')
    elif col_2 in df.columns:
        # Solo existe col_2
        df[descripcion_limpia] = df[col_2].fillna('')
    else:
        # Ninguna columna existe, manejar error
        raise ValueError("Error: Ninguna de las columnas especificadas existe en el DataFrame.")

    return df

def procesar_descripcion(data, nombre_columna):
    """
    Procesa una columna de un DataFrame aplicando normalización y manejo de combinaciones de texto.
    
    Parámetros:
    - data: DataFrame que contiene la columna a procesar.
    - nombre_columna: Nombre de la columna que se va a procesar.
    
    Retorna:
    - DataFrame con la columna procesada y actualizada.
    """
    # Verificar si la columna existe en el DataFrame
    if nombre_columna not in data.columns:
        raise KeyError(f"La columna '{nombre_columna}' no existe en el DataFrame.")
    
    # Función para normalizar el texto
    def normalizar(texto):
        # Asegurar que el texto sea un string
        texto = str(texto).strip().lower()
        
        # 1. Eliminar espacios redundantes
        texto = re.sub(r'\s+', ' ', texto)

        # 2. Remover caracteres especiales excepto letras, números, espacios y '%'
        texto = re.sub(r'[^a-zA-Z0-9\s%]', '', texto)

        # 3. Separar números de letras y letras de números
        texto = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', texto)
        texto = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', texto)

        # 4. Manejo de 'x':
        texto = re.sub(r'(?<=\d)x(?=\d)', r' x ', texto)  # separar x entre números
        texto = re.sub(r'\b([a-zA-Z]+)x\b', r'\1 x', texto)  # separar palabras terminadas en x

        # 5. Reemplazar separadores como guiones o barras con espacios
        texto = re.sub(r'[-/]', ' ', texto)

        # 6. Manejo de unidades (por ejemplo, separar g, ml, etc. de los números)
        texto = re.sub(r'(\d+)\s*([a-zA-Z]+)', r'\1 \2', texto)

        # 7. Eliminar espacios redundantes nuevamente
        texto = re.sub(r'\s+', ' ', texto).strip()  # <- Aquí se eliminan dobles espacios

        # 8. Combinaciones
        combinaciones = {
            'anemido x': 'anemidox',
            'jgaprell' : 'jeringa prellenada',
            'fle x': 'flex',
            'argeflo x':'argeflox',
            'aropa x': 'aropax',
            'arolte x' : 'aroltex',
            'atopi x':  'atopix',
            'atorma x': 'atormax',
            'comprec': 'comp recubierto',
            'soloft': 'solucion oftalmica',
            'g': 'gr',
            'cr': 'crema',
            'comp' : 'comprimidos',
            'caps': 'capsulas',
            "jer.pre" : "jeringa prellenada",
            "mg" : "miligramos",
            "ml" : "mililitros",
            "mm" : "milimetros",
            'zyvo x': 'zyvox',
            'loc' : 'locion',
            "gr" : "gramos",
            "jga" : 'jeringa',
            "cm" : 'centimetros',
            'u' : "unidad",
            'shamp' : 'shampoo',
            "unid" : " unidad",
            'cep' : 'cepillo dental',
            "emuls prot" : 'emulsion protectora',
            'emulshidrat':'emulsion hidratante',
            'emulshumect' : "emulsion humectante",
            'iny': 'inyeccion',
            'amp' : 'ampolla',
            'inylioffa': 'inyeccion lioffa',
            'ds' : 'dosis',
            'inyfa': 'inyeccion fa',
            'jbe': 'jarabe',
            'blist': 'blister',
            'sob' : 'sobres',
            'fa': 'frasco ampolla',
            'jab' : 'jabon',
            'cps' :'capsulas',
            'ivi x' : 'ivix',
            'inya': 'inyectable',
            'inyjgaprell' : 'iny jeringa prellenada',
            'mcg': 'microgramo',
            'gts': 'gotas',
            'mgml' : 'miligramos por mililitro',
            'env': 'envase',
            'gtsoft' : 'gotas oftálmicas',
            'compdisp': 'comprimidos disp',
            'comprecran' : 'comprimidos recubiertos ranurados',
            'sol': 'solucion',
            'jgapre': 'jeringa prellenada',
            'fcocps' : 'frasco capsulas',
            'fcogotero' : 'frasco gotero',
            'fco': 'frasco', 
            'solspray' : 'solucion spray',
            'solpuas' : 'sol puas',
            'cpsblandas' : 'cps blandas',
            'tab' : 'tableta',
            'sach' : 'sachet',
            'mgvial': 'miligramos vial',
            'cpsbl' :'capsula blanda',
            'zyvali x': 'zyvalix',
            'x' : 'por',
            'lapprell': 'lapicera prellenada',
            'complibprol' : 'comp lib prolongada',
            'compcu': 'comp cu',
            'jerprell'  : "jeringa prellenada",
            'prell': 'prellenada',
            'drenabprecortconv': 'drenable precorte conve',
            'drenabprecortopac': 'drenable precorte opac '        
        }
        for key, val in combinaciones.items():
            texto = re.sub(rf'\b{key}\b', val, texto)

        # 9. Eliminar cualquier doble espacio que haya quedado después de los reemplazos
        texto = re.sub(r'\s+', ' ', texto).strip()

        return texto

    # Aplicar la función 'normalizar' a cada elemento de la columna
    data[nombre_columna] = data[nombre_columna].apply(normalizar)
    
    return data