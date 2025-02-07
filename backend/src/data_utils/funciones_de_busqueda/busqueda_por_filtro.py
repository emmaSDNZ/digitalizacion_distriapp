def filtrar_por_laboratorio(df, laboratorio_input, columna_laboratorio='atrib0'):
    """
    Filtra los productos de un DataFrame (df) según el nombre del laboratorio proporcionado.

    Esta función busca coincidencias exactas entre el nombre del laboratorio proporcionado 
    (laboratorio_input) y los valores de la columna especificada en el DataFrame (por defecto 'atrib0').
    La comparación es insensible a mayúsculas y minúsculas.

    Parámetros:
    - df (DataFrame): El DataFrame que contiene los productos a filtrar.
    - laboratorio_input (str): El nombre del laboratorio que se busca en el DataFrame.
    - columna_laboratorio (str, opcional): El nombre de la columna que contiene los nombres de los laboratorios. 
      Por defecto es 'atrib0'.

    Retorna:
    - DataFrame: Un DataFrame filtrado que contiene solo los productos que coinciden con el laboratorio.
    - None: Si no se encuentran coincidencias.

    """
    
    # Convertir tanto la columna de laboratorios como el input a minúsculas para hacer la comparación insensible a mayúsculas
    df_filtrado = df[df[columna_laboratorio].str.lower() == laboratorio_input.lower()]
    
    if not df_filtrado.empty:
        print(f"Se encontraron {len(df_filtrado)} productos coincidentes del laboratorio '{laboratorio_input}'.")
        return df_filtrado
    else:
        print(f"No se encontraron productos del laboratorio '{laboratorio_input}'.")
        return None
