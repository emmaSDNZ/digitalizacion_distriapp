#Funcion para obtener las coincidencias entre dos columnas

def column_to_match(column_productos, column_proveedor):
    """
    Para esta feature usamos como ejemplo de limpieza la columna Descripcion de ambos CSV

    """

    """
    Función para obtener las coincidencias entre dos columnas de descripciones
    """
    # Asegurarse de que ambas columnas sean cadenas de texto
    column_productos = column_productos.astype(str).fillna('')
    print(column_productos)
    column_proveedor = column_proveedor.astype(str).fillna('')
    
    # Buscar coincidencias usando apply
    to_match = column_productos[column_productos.apply(lambda x: any(proveedor.lower() in x.lower() for proveedor in column_proveedor))]
    
    return to_match