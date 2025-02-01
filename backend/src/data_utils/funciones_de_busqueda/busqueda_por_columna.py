import pandas as pd

def busqueda_codigo_por_columna(df_master, df_proveedor, columna_codigo_master, columna_codigo_proveedor):
    """
    Función que procesa el código de producto del proveedor y lo combina con el DataFrame Master según el código de producto.
    
    Parámetros:
    - df_Proveedor_cod_prod (DataFrame): DataFrame con los datos del proveedor.
    - df_MasterProductos_Filtro_cod_prod (DataFrame): DataFrame Master con los datos de productos.
    - columna_codigo_master (str): Nombre de la columna que contiene el código de producto o codigo de barra del Master.
    - columna_niprod (str): Nombre de la columna que contiene el código 'niprod' en el DataFrame Master.
    - columna_codigo_proveedor (str): Nombre de la columna que contiene el código de producto o codigo de barra del proveedor.
    
    Retorna:
    - DataFrame: El DataFrame procesado con la columna 'niprod' agregada si se realiza el merge.
    - DataFrame: El DataFrame sin cambios si no se encuentra coicidencias.
    """
    
    # Verificar si la columna del código de producto del proveedor existe en el DataFrame del proveedor
    if columna_codigo_proveedor in df_proveedor.columns:
    
        # Filtrar los valores que no son 'nan' en el DataFrame del proveedor
        df_Proveedor_cod_prod_filtro = df_proveedor
        
        # Verificar si el DataFrame del Master (productos) no está vacío
        if not df_master.empty:
            print(f"Se inicia proceso de búsqueda por código de barras en la columna {columna_codigo_proveedor}")
            
            """ 
            Código para realizar el 'merge' entre el DataFrame del proveedor y el DataFrame Master,
            uniendo los datos según el código de productos.
            """
            # Verificar si existen coincidencias entre los códigos de productos de proveedor y master
            if df_Proveedor_cod_prod_filtro[columna_codigo_proveedor].isin(df_master[columna_codigo_master]).any():
                print("Se encontraron coincidencias")
                
                # Verificar si la columna 'niprod' ya está presente en el DataFrame del proveedor
                if 'niprod' not in df_Proveedor_cod_prod_filtro.columns:
                    # Realizar el 'merge' solo si 'niprod' no está presente en el DataFrame
                    df_Proveedor_cod_prod_filtro = pd.merge(
                        df_Proveedor_cod_prod_filtro,
                        df_master[[columna_codigo_master, 'niprod']],  # Selección de columnas para 'merge'
                        left_on=columna_codigo_proveedor,  # Columna en proveedor para hacer el join
                        right_on=columna_codigo_master,  # Columna en master para hacer el join
                        how='left'  # Tipo de join ('inner' para encontrar solo coincidencias)
                    )
                else:
                    # Si 'niprod' ya está presente en el DataFrame, no realizar el 'merge' nuevamente
                    print("Ya existe la columna 'niprod' en el dataframe de proveedor")
            else:
                # Si no se encuentran coincidencias entre los códigos de barras
                print("No se encontraron coincidencias")
                return df_proveedor
            
            # Devolver el DataFrame con los datos después del 'merge' (si es que se ha realizado)
            return df_Proveedor_cod_prod_filtro
        else:
            # Si el DataFrame Master está vacío, mostrar mensaje
            print(f"No hay valores válidos en la columna {columna_codigo_proveedor}")
            return df_Proveedor_cod_prod_filtro  # Retornar el DataFrame sin cambios
    else:
        # Si no se encuentra la columna de código de barras del proveedor en el DataFrame
        print(f"No existe la columna {columna_codigo_proveedor} en el archivo de proveedor")
        return df_Proveedor_cod_prod_filtro  # Retornar el DataFrame sin cambios
