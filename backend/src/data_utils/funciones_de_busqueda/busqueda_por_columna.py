import pandas as pd

def busqueda_codigo_por_columna(df_master, df_proveedor, columna_codigo_master, columna_codigo_proveedor):
    """
    Función que procesa el código de producto del proveedor y lo combina con el DataFrame Master según el código de producto.
    
    Parámetros:
    - df_master (DataFrame): DataFrame Master con los datos de productos.
    - df_proveedor (DataFrame): DataFrame con los datos del proveedor.
    - columna_codigo_master (str): Nombre de la columna que contiene el código de producto o código de barra del Master.
    - columna_codigo_proveedor (str): Nombre de la columna que contiene el código de producto o código de barra del proveedor.
    
    Retorna:
    - df_original (DataFrame): DataFrame del proveedor con la columna 'niprod' agregada después del merge.
    - df_coincidentes (DataFrame): DataFrame con solo las filas que tienen coincidencias en 'niprod'.
    - df_no_coincidentes (DataFrame): DataFrame con solo las filas sin coincidencias en 'niprod'.
    """
    
    df_original = df_proveedor.copy()  # Copia del DataFrame original

    if columna_codigo_proveedor not in df_proveedor.columns:
        print(f"La columna {columna_codigo_proveedor} no existe en el DataFrame del proveedor.")
        return df_original, pd.DataFrame(), pd.DataFrame()

    if df_master.empty:
        print("El DataFrame Master está vacío.")
        return df_original, pd.DataFrame(), pd.DataFrame()

    print(f"Se inicia proceso de búsqueda por código de barras en la columna {columna_codigo_proveedor}")

    if df_original[columna_codigo_proveedor].isin(df_master[columna_codigo_master]).any():
        print("Se encontraron coincidencias")

        # Verificar si la columna 'niprod' ya está presente en el DataFrame del proveedor
        if 'niprod' not in df_original.columns:
            df_original = df_original.merge(
                df_master[[columna_codigo_master, 'niprod']],  
                left_on=columna_codigo_proveedor,  
                right_on=columna_codigo_master,  
                how='left'  
            )
        else:
            print("Ya existe la columna 'niprod' en el DataFrame de proveedor")
    else:
        print("No se encontraron coincidencias")
        return df_original, pd.DataFrame(), pd.DataFrame()

    # Separar en dos DataFrames según si 'niprod' tiene o no un valor
    df_coincidentes = df_original[df_original['niprod'].notna()]
    df_no_coincidentes = df_original[df_original['niprod'].isna()]

    # Retornar los tres DataFrames:
    return df_original, df_coincidentes, df_no_coincidentes