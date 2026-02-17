def manejar_objecion(texto_usuario):
    """
    Skill: Venta Consultiva
    Objetivo: Rebatir objeciones comunes (precio, confianza) con valor agregado.
    """
    texto = texto_usuario.lower()
    
    if any(palabra in texto for palabra in ["caro", "precio", "descuento", "rebaja"]):
        return {
            "respuesta": (
                "💸 *Entiendo perfectamente.* Por eso mismo tenemos el **10% OFF por transferencia** "
                "por tiempo limitado. ¡Es el mejor momento para aprovecharlo!\n\n"
                "📌 *Dato:* Ya entregamos 5 pares hoy solo en Grand Bourg. ¡No te quedes sin las tuyas!"
            )
        }
    
    if any(palabra in texto for palabra in ["confianza", "original", "truchas", "calidad", "garantia"]):
        return {
            "respuesta": (
                "🇧🇷 **Garantía de Calidad:** Son **Originales de Brasil**, la más alta calidad de la zona.\n\n"
                "✅ Además, tenés **garantía de cambio por talle** directamente en el punto de encuentro. "
                "¡Tu satisfacción es nuestra prioridad!"
            )
        }
    
    return None
