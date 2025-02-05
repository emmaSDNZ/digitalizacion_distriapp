def verificar_columnas_proveedor(df):
    """
    Verifica si un DataFrame (df) contiene las columnas obligatorias para un proveedor.

    Args:
        df (pd.DataFrame): El DataFrame de pandas a verificar.

    Returns:
        bool: True si todas las columnas requeridas están presentes, False en caso contrario.
              Imprime mensajes a la consola indicando qué columnas faltan (si alguna).
    """

    # Lista de las columnas requeridas para los datos del proveedor.
    columnas_requeridas = [
        "xx_cod_de_producto",  # Código del producto.
        "xx_cod_de_barra",  # Código de barras del producto.
        "xx_descripcion",  # Descripción del producto.
        "xx_presentación",  # Presentación del producto (ej: caja, unidad, etc.).
        "xx_unidad",  # Unidad de medida del producto (ej: kg, l, unidades, etc.).
        "xx_contenido",  # Contenido del producto (ej: cantidad, peso, volumen, etc.).
        "xx_laboratorio",  # Laboratorio fabricante del producto.
        "xx_precio_base",  # Precio base del producto.
        "xx_precio_iva"  # Precio del producto con IVA.
    ]

    # Crea una lista con las columnas que *faltan* en el DataFrame.
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]

    # Si hay columnas faltantes...
    if columnas_faltantes:
        print("Error: Las siguientes columnas faltan en el DataFrame:")
        print(columnas_faltantes)  # Imprime la lista de columnas faltantes.
        return False  # Retorna False para indicar que no están todas las columnas.
        # Se podría lanzar una excepción aquí con:
        # raise ValueError("Debe agregar las columnas faltantes antes de continuar.")
    else:
        print("Todas las columnas requeridas están presentes.")  # Imprime mensaje si están todas.
        return True  # Retorna True si están todas las columnas.