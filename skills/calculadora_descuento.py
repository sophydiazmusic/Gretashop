def calcular_descuento_transferencia(precio_lista):
    """
    Skill: Calculadora de Descuento
    Objetivo: Calcular el 10% OFF por pago mediante transferencia.
    """
    try:
        precio = float(precio_lista)
        descuento = precio * 0.10
        precio_con_descuento = precio - descuento
        
        # Formateamos los números para que se vean bien (con separador de miles opcional, pero limpio)
        precio_formateado = f"{precio:,.0f}".replace(",", ".")
        precio_final_formateado = f"{precio_con_descuento:,.0f}".replace(",", ".")
        
        etiqueta_oferta = " ¡OFERTA! 🔥" if precio_con_descuento < 45000 else ""
        
        return {
            "exito": True,
            "mensaje": f"El precio de lista es ${precio_formateado}. Pero si aprovechás el 10% OFF por transferencia, te quedan en solo **${precio_final_formateado}**{etiqueta_oferta}",
            "precio_original": precio,
            "precio_final": precio_con_descuento,
            "es_oferta": precio_con_descuento < 45000
        }
    except (ValueError, TypeError):
        return {
            "exito": False,
            "mensaje": "Hubo un error al calcular el descuento. Por favor, ingresá un valor numérico válido.",
            "precio_original": None,
            "precio_final": None
        }
