def clasificar_zona_entrega(zona_usuario):
    """
    Skill: Detector de Zona
    Objetivo: Clasificar si es Punto de Encuentro (Gratis) o Envío por Correo.
    """
    # --- CONFIGURACIÓN DE ZONAS GRATIS ---
    ZONAS_GRATUITAS = {
        "grand bourg": ["g. bourg", "grand burg", "bourg"],
        "moron": ["moron", "morón"],
        "san miguel": ["san mi", "miguel"],
        "caballito": ["caba", "cabaillito"],
        "el triangulo": ["triangulo", "el tri"]
    }
    # -------------------------------------
    
    zona_limpia = zona_usuario.lower().strip()
    
    # Lógica de Fuzzy Matching (coincidencia de palabras clave)
    zona_oficial = None
    for oficial, variantes in ZONAS_GRATUITAS.items():
        if oficial in zona_limpia or any(v in zona_limpia for v in variantes):
            zona_oficial = oficial
            break
    
    if zona_oficial:
        nombre_zona = str(zona_oficial).title()
        return {
            "tipo": "Gratis",
            "mensaje": f"¡Genial! En *{nombre_zona}* entregamos **sin cargo** en punto de encuentro. 📍",
            "zona_detectada": zona_oficial
        }
    else:
        return {
            "tipo": "Correo",
            "mensaje": "Para esa zona el envío es por **Correo Argentino**. El costo se calcula según el peso del paquete.",
            "zona_detectada": zona_limpia
        }
