from decimal import Decimal

def convertir_unidades(cantidad, unidad_origen, unidad_destino):
    # Diccionarios de conversiones (todos los valores son Decimal)
    conversiones_masa = {
        "kg": Decimal('1.0'),
        "g": Decimal('1000.0'),
        "mg": Decimal('1000000.0'),
        "lb": Decimal('2.20462'),  # 1 kg = 2.20462 lb
    }

    conversiones_volumen = {
        "L": Decimal('1.0'),
        "mL": Decimal('1000.0'),
        "cm³": Decimal('1000.0'),
        "m³": Decimal('0.001'),
        "gal": Decimal('0.264172'),  # 1 L = 0.264172 galón
    }

    conversiones_longitud = {
        "m": Decimal('1.0'),     # 1 m = 1 metro
        "mm": Decimal('0.001'),  # 1 mm = 0.001 metros
        "cm": Decimal('0.01'),   # 1 cm = 0.01 metros
        "in": Decimal('0.0254'), # 1 pulgada = 0.0254 metros
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
        cantidad_en_metros = cantidad * conversiones_longitud[unidad_origen]  # Convertir a metros
        return cantidad_en_metros / conversiones_longitud[unidad_destino]  # Convertir a la unidad destino

    # Si no se puede convertir, lanza un error
    raise ValueError(f"No se puede convertir de {unidad_origen} a {unidad_destino}")