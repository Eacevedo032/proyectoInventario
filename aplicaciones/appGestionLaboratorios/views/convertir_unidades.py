# Función para convertir unidades
def convertir_unidades(cantidad, unidad_origen, unidad_destino, densidad=None):
    # Diccionarios de conversiones
    conversiones_masa = {
        "kg": 1,
        "g": 1000,
        "mg": 1_000_000,
        "t": 0.001,
    }

    conversiones_volumen = {
        "L": 1,
        "mL": 1000,
        "cm³": 1000,
        "m³": 0.001,
    }

    conversiones_longitud = {
        "mm": 0.001,
        "cm": 0.01,
        "m": 1,
        "km": 1000,
    }

    # Conversión entre masa
    if unidad_origen in conversiones_masa and unidad_destino in conversiones_masa:
        cantidad_en_kg = cantidad / conversiones_masa[unidad_origen]
        return cantidad_en_kg * conversiones_masa[unidad_destino]

    # Conversión entre volumen
    elif unidad_origen in conversiones_volumen and unidad_destino in conversiones_volumen:
        cantidad_en_litros = cantidad / conversiones_volumen[unidad_origen]
        return cantidad_en_litros * conversiones_volumen[unidad_destino]

    # Conversión entre longitud
    elif unidad_origen in conversiones_longitud and unidad_destino in conversiones_longitud:
        cantidad_en_metros = cantidad / conversiones_longitud[unidad_origen]
        return cantidad_en_metros * conversiones_longitud[unidad_destino]

    # Conversión entre masa y volumen (usando densidad)
    elif densidad is not None:
        if unidad_origen in conversiones_masa and unidad_destino in conversiones_volumen:
            cantidad_en_kg = cantidad / conversiones_masa[unidad_origen]
            volumen_en_litros = cantidad_en_kg / densidad
            return volumen_en_litros * conversiones_volumen[unidad_destino]

        elif unidad_origen in conversiones_volumen and unidad_destino in conversiones_masa:
            cantidad_en_litros = cantidad / conversiones_volumen[unidad_origen]
            masa_en_kg = cantidad_en_litros * densidad
            return masa_en_kg * conversiones_masa[unidad_destino]

    # Si no se puede convertir, lanza un error
    raise ValueError(f"No se puede convertir de {unidad_origen} a {unidad_destino}")
