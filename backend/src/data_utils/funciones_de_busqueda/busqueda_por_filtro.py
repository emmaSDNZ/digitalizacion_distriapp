
# Función para filtrar los productos según el laboratorio ingresado (sin importar mayúsculas/minúsculas)

def filtrar_por_laboratorio(df, laboratorio_input, columna_laboratorio='atrib0'):

    # Convertir tanto la columna de laboratorios como el input a minúsculas para hacer la comparación insensible a mayúsculas
    
    df_filtrado = df[df[columna_laboratorio].str.lower() == laboratorio_input.lower()]
    if not df_filtrado.empty:
        print(f"Se encontraron {len(df_filtrado)} productos coincidentes del laboratorio '{laboratorio_input}'.")
        return df_filtrado
    else:
        print(f"No se encontraron productos del laboratorio '{laboratorio_input}'.")
        return None

