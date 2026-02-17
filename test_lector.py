import sys
from skills.lector_productos import cargar_productos_desde_csv, obtener_catalogo_unico, obtener_talles_disponibles

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def test_lector():
    ruta = "zapatillas_greta.csv"
    inventario = cargar_productos_desde_csv(ruta)
    
    if not inventario:
        print("❌ Error: No se cargaron productos.")
        return

    print(f"✅ Se cargaron {len(inventario)} registros de productos.")
    
    catalogo = obtener_catalogo_unico(inventario)
    print(f"📦 Modelos únicos encontrados: {len(catalogo)}")
    print(f"Ejemplo de catálogo: {catalogo[:3]}")
    
    if catalogo:
        primer_modelo = catalogo[0]
        talles = obtener_talles_disponibles(inventario, primer_modelo)
        print(f"👟 Talles para {primer_modelo}: {talles}")

if __name__ == "__main__":
    test_lector()
