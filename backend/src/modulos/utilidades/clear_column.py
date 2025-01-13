import re

# Función para limpiar y normalizar las descripciones
def clear_column(column):
    """
    Limpiar la columna de descripciones para eliminar términos irrelevantes y normalizar el texto.
    """
    # Regex mejorado para eliminar números, unidades, caracteres especiales y otros términos irrelevantes
    columna_limpia = re.sub(r'\b(\d+|mg|comp\.|blisters|estuche|x|ml|unidades|marca|botella|caja|referencia|cm|g|m|f\.a\.x|jbe\.|sol\.|env\.|lata|vial|pvo\.|sobres|gotero|cápsulas|frascos|blister|bot\.)\b', '', column, flags=re.IGNORECASE)

    # Eliminar caracteres especiales como los dos puntos, puntos finales, comas y otros símbolos
    columna_limpia = re.sub(r'[:\.\-,]', '', columna_limpia)  # Eliminamos puntos, comas y dos puntos

    # Eliminar múltiples espacios en blanco y normalizar la columna
    columna_limpia = re.sub(r'\s+', ' ', columna_limpia).strip()

    # Convertir todo el texto a minúsculas
    columna_limpia = columna_limpia.lower()

    return columna_limpia

