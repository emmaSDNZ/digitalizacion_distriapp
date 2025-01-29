
def indexar_productos(df, index_col):
    """
    Agrega un índice único a cada producto dentro del DataFrame.

    Parámetros:
        df (pd.DataFrame): DataFrame con los datos.
        index_col (str): Nombre de la columna donde se almacenará el índice.

    Retorna:
        pd.DataFrame: DataFrame con la columna de índice asignada.
    """
    df[index_col] = df.index
    return df