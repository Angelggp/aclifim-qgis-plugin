"""
Script de Prueba para Bases de Datos Access con Contraseña

Este script te ayuda a verificar:
1. Si tu base de datos Access tiene contraseña
2. Qué tipo de contraseña tiene
3. Si el driver ODBC está instalado correctamente

Uso:
    python probar_conexion_access.py ruta/a/base.mdb
    python probar_conexion_access.py ruta/a/base.accdb contraseña_opcional
"""

import sys
import os


def probar_conexion(archivo, password=None):
    """
    Prueba la conexión a una base de datos Access
    
    Args:
        archivo: ruta al archivo .mdb o .accdb
        password: contraseña opcional
    """
    print("="*80)
    print("PRUEBA DE CONEXIÓN A ACCESS")
    print("="*80)
    print(f"\nArchivo: {archivo}")
    print(f"Contraseña: {'Sí (' + '*' * len(password) + ')' if password else 'No'}")
    print()
    
    # Verificar que el archivo existe
    if not os.path.exists(archivo):
        print("❌ ERROR: El archivo no existe")
        return False
    
    # Verificar extensión
    ext = os.path.splitext(archivo)[1].lower()
    if ext not in ['.mdb', '.accdb']:
        print(f"⚠️  ADVERTENCIA: Extensión '{ext}' no es .mdb ni .accdb")
    
    # Intentar importar pyodbc
    print("1. Verificando pyodbc...")
    try:
        import pyodbc
        print(f"   ✅ pyodbc {pyodbc.version} instalado")
    except ImportError:
        print("   ❌ pyodbc NO está instalado")
        print("   Instala con: pip install pyodbc")
        return False
    
    # Verificar drivers disponibles
    print("\n2. Verificando drivers ODBC de Access...")
    drivers = [d for d in pyodbc.drivers() if 'Access' in d or 'accdb' in d.lower()]
    
    if not drivers:
        print("   ❌ No se encontró driver ODBC de Access")
        print("   Descarga: https://www.microsoft.com/en-us/download/details.aspx?id=54920")
        return False
    
    print(f"   ✅ Driver(s) encontrado(s):")
    for driver in drivers:
        print(f"      • {driver}")
    
    driver = drivers[0]
    
    # Probar conexión sin contraseña
    print("\n3. Probando conexión SIN contraseña...")
    conn_str = f'DRIVER={{{driver}}};DBQ={archivo};'
    
    try:
        conn = pyodbc.connect(conn_str)
        conn.close()
        print("   ✅ CONEXIÓN EXITOSA sin contraseña")
        print("   → La base de datos NO tiene contraseña")
        return True
    except pyodbc.Error as e:
        error_msg = str(e).lower()
        if "password" in error_msg or "cannot open" in error_msg:
            print("   ⚠️  Base de datos protegida con contraseña")
        else:
            print(f"   ❌ Error: {e}")
            return False
    
    # Si llegamos aquí, necesita contraseña
    if not password:
        print("\n   ℹ️  Vuelve a ejecutar el script con la contraseña:")
        print(f"      python {sys.argv[0]} \"{archivo}\" tu_contraseña")
        return False
    
    # Probar con contraseña - método 1: PWD
    print(f"\n4. Probando conexión con contraseña...")
    print("   Método 1: PWD=password")
    conn_str = f'DRIVER={{{driver}}};DBQ={archivo};PWD={password};'
    
    try:
        conn = pyodbc.connect(conn_str)
        conn.close()
        print("   ✅ CONEXIÓN EXITOSA con PWD=password")
        print("   → Tipo: Contraseña de usuario (más común)")
        return True
    except pyodbc.Error as e:
        print(f"   ❌ Falló: {e}")
    
    # Método 2: UID+PWD
    print("   Método 2: UID=Admin;PWD=password")
    conn_str = f'DRIVER={{{driver}}};DBQ={archivo};UID=Admin;PWD={password};'
    
    try:
        conn = pyodbc.connect(conn_str)
        conn.close()
        print("   ✅ CONEXIÓN EXITOSA con UID=Admin;PWD=password")
        print("   → Tipo: Usuario + Contraseña")
        return True
    except pyodbc.Error as e:
        print(f"   ❌ Falló: {e}")
    
    # Método 3: Database Password
    print("   Método 3: Database Password=password")
    conn_str = f'DRIVER={{{driver}}};DBQ={archivo};Database Password={password};'
    
    try:
        conn = pyodbc.connect(conn_str)
        conn.close()
        print("   ✅ CONEXIÓN EXITOSA con Database Password=password")
        print("   → Tipo: Cifrado completo de base de datos")
        return True
    except pyodbc.Error as e:
        print(f"   ❌ Falló: {e}")
    
    # Si todos fallaron
    print("\n   ❌ NINGÚN MÉTODO FUNCIONÓ")
    print("   Posibles causas:")
    print("   • Contraseña incorrecta")
    print("   • Base de datos corrupta")
    print("   • Tipo de protección no estándar")
    print("\n   Sugerencias:")
    print("   1. Verifica que la contraseña sea correcta (case-sensitive)")
    print("   2. Intenta abrir la BD en Microsoft Access primero")
    print("   3. Si Access pide reparar, hazlo y vuelve a intentar")
    
    return False


def listar_tablas(archivo, password=None):
    """Lista las tablas disponibles en la base de datos"""
    try:
        import pyodbc
    except ImportError:
        return
    
    print("\n" + "="*80)
    print("LISTANDO TABLAS")
    print("="*80)
    
    drivers = [d for d in pyodbc.drivers() if 'Access' in d]
    if not drivers:
        print("❌ No hay driver ODBC de Access")
        return
    
    driver = drivers[0]
    
    # Probar conexiones según tenga o no contraseña
    conexiones_probar = []
    if password:
        conexiones_probar = [
            f'DRIVER={{{driver}}};DBQ={archivo};PWD={password};',
            f'DRIVER={{{driver}}};DBQ={archivo};UID=Admin;PWD={password};',
            f'DRIVER={{{driver}}};DBQ={archivo};Database Password={password};',
        ]
    else:
        conexiones_probar = [f'DRIVER={{{driver}}};DBQ={archivo};']
    
    conn = None
    for conn_str in conexiones_probar:
        try:
            conn = pyodbc.connect(conn_str)
            break
        except:
            continue
    
    if not conn:
        print("❌ No se pudo conectar para listar tablas")
        return
    
    try:
        cursor = conn.cursor()
        tablas = []
        
        for table_info in cursor.tables(tableType='TABLE'):
            nombre = table_info.table_name
            # Filtrar tablas del sistema
            if not nombre.startswith('MSys') and not nombre.startswith('~'):
                tablas.append(nombre)
        
        print(f"\n✅ Se encontraron {len(tablas)} tablas (sin contar tablas del sistema):")
        for i, tabla in enumerate(tablas, 1):
            marcador = " ← ACLIFIM!" if 'ACLIFIM' in tabla.upper() else ""
            print(f"   {i}. {tabla}{marcador}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listando tablas: {e}")


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python probar_conexion_access.py <archivo.mdb|archivo.accdb> [contraseña]")
        print("\nEjemplos:")
        print("  python probar_conexion_access.py base_datos.mdb")
        print("  python probar_conexion_access.py base_datos.accdb mi_contraseña")
        sys.exit(1)
    
    archivo = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Probar conexión
    success = probar_conexion(archivo, password)
    
    # Si fue exitoso, listar tablas
    if success:
        listar_tablas(archivo, password)
    
    print("\n" + "="*80)
    if success:
        print("✅ PRUEBA EXITOSA - El plugin debería poder importar esta base de datos")
    else:
        print("❌ PRUEBA FALLIDA - Resuelve los problemas antes de importar en el plugin")
    print("="*80)


if __name__ == "__main__":
    main()
