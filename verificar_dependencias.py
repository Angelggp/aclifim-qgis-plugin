"""
Script de Verificación de Dependencias
Plugin de Gestión de Afiliados para QGIS

Ejecuta verificaciones automáticas de todos los requisitos del sistema.
Genera un reporte detallado con el estado de cada componente.

Uso:
    python verificar_dependencias.py
    
    o desde QGIS Python Console:
    exec(open('path/to/verificar_dependencias.py').read())
"""

import sys
import platform
import subprocess
import importlib.util
from datetime import datetime


class Colors:
    """Códigos ANSI para colores en consola (Windows 10+ y Unix)"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'
    
    @staticmethod
    def supports_color():
        """Detecta si la terminal soporta colores"""
        if platform.system() == "Windows":
            # Windows 10+ soporta ANSI
            return platform.release() in ['10', '11']
        return True


# Si no soporta colores, usar strings vacíos
if not Colors.supports_color():
    Colors.GREEN = Colors.YELLOW = Colors.RED = Colors.BLUE = Colors.BOLD = Colors.END = ''


class DependencyChecker:
    """Verifica dependencias del sistema"""
    
    def __init__(self):
        self.results = []
        self.warnings = []
        self.errors = []
    
    def check(self, name, test_func, critical=True):
        """
        Ejecuta una verificación y registra el resultado
        
        Args:
            name: nombre de la verificación
            test_func: función que retorna (bool, str) - (éxito, mensaje)
            critical: si es crítico (error) o no (warning)
        """
        try:
            success, message = test_func()
            status = "✓" if success else ("✗" if critical else "⚠")
            color = Colors.GREEN if success else (Colors.RED if critical else Colors.YELLOW)
            
            self.results.append({
                'name': name,
                'success': success,
                'message': message,
                'critical': critical,
                'status': status,
                'color': color
            })
            
            if not success:
                if critical:
                    self.errors.append(f"{name}: {message}")
                else:
                    self.warnings.append(f"{name}: {message}")
            
            return success
        except Exception as e:
            self.results.append({
                'name': name,
                'success': False,
                'message': f"Error en verificación: {str(e)}",
                'critical': critical,
                'status': "✗",
                'color': Colors.RED
            })
            if critical:
                self.errors.append(f"{name}: Error en verificación")
            return False
    
    def print_results(self):
        """Imprime resultados de todas las verificaciones"""
        print("\n" + "="*80)
        print(f"{Colors.BOLD}VERIFICACIÓN DE DEPENDENCIAS - PLUGIN DE GESTIÓN DE AFILIADOS{Colors.END}")
        print("="*80 + "\n")
        
        for result in self.results:
            status_colored = f"{result['color']}{result['status']}{Colors.END}"
            print(f"{status_colored} {Colors.BOLD}{result['name']}{Colors.END}")
            print(f"   {result['message']}\n")
        
        # Resumen
        print("="*80)
        total = len(self.results)
        success = sum(1 for r in self.results if r['success'])
        failed = total - success
        
        print(f"{Colors.BOLD}RESUMEN:{Colors.END}")
        print(f"  Total de verificaciones: {total}")
        print(f"  {Colors.GREEN}Exitosas: {success}{Colors.END}")
        if failed > 0:
            print(f"  {Colors.RED}Fallidas: {failed}{Colors.END}")
        
        if self.errors:
            print(f"\n{Colors.RED}{Colors.BOLD}ERRORES CRÍTICOS ({len(self.errors)}):{Colors.END}")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}ADVERTENCIAS ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("\n" + "="*80)
        
        if not self.errors:
            print(f"{Colors.GREEN}{Colors.BOLD}✓ TODOS LOS REQUISITOS CRÍTICOS ESTÁN SATISFECHOS{Colors.END}")
            if self.warnings:
                print(f"{Colors.YELLOW}⚠ Hay algunas advertencias que pueden afectar funcionalidades opcionales{Colors.END}")
            print("\nEl plugin debería funcionar correctamente.")
        else:
            print(f"{Colors.RED}{Colors.BOLD}✗ HAY REQUISITOS CRÍTICOS FALTANTES{Colors.END}")
            print("\nPor favor, resuelva los errores antes de usar el plugin.")
            print("Consulte REQUISITOS_SISTEMA.md y TROUBLESHOOTING.md para más información.")
        
        print("="*80 + "\n")
    
    def save_report(self, filename='verificacion_dependencias.txt'):
        """Guarda el reporte en un archivo"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("VERIFICACIÓN DE DEPENDENCIAS - PLUGIN DE GESTIÓN DE AFILIADOS\n")
                f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("="*80 + "\n\n")
                
                for result in self.results:
                    f.write(f"{result['status']} {result['name']}\n")
                    f.write(f"   {result['message']}\n\n")
                
                f.write("="*80 + "\n")
                f.write("RESUMEN:\n")
                f.write(f"  Total: {len(self.results)}\n")
                f.write(f"  Exitosas: {sum(1 for r in self.results if r['success'])}\n")
                f.write(f"  Fallidas: {len(self.results) - sum(1 for r in self.results if r['success'])}\n")
                
                if self.errors:
                    f.write(f"\nERRORES CRÍTICOS ({len(self.errors)}):\n")
                    for error in self.errors:
                        f.write(f"  - {error}\n")
                
                if self.warnings:
                    f.write(f"\nADVERTENCIAS ({len(self.warnings)}):\n")
                    for warning in self.warnings:
                        f.write(f"  - {warning}\n")
            
            print(f"Reporte guardado en: {filename}")
            return True
        except Exception as e:
            print(f"Error guardando reporte: {e}")
            return False


# ============================================================================
# FUNCIONES DE VERIFICACIÓN
# ============================================================================

def check_python_version():
    """Verifica versión de Python"""
    major = sys.version_info.major
    minor = sys.version_info.minor
    version = f"{major}.{minor}.{sys.version_info.micro}"
    
    if major >= 3 and minor >= 7:
        return True, f"Python {version} (OK)"
    else:
        return False, f"Python {version} - Se requiere Python 3.7 o superior"


def check_operating_system():
    """Verifica sistema operativo"""
    os_name = platform.system()
    os_version = platform.release()
    return True, f"{os_name} {os_version}"


def check_pyqt5():
    """Verifica instalación de PyQt5"""
    try:
        import PyQt5.QtCore
        version = PyQt5.QtCore.QT_VERSION_STR
        return True, f"PyQt5 instalado (Qt {version})"
    except ImportError:
        return False, "PyQt5 no está instalado - Requerido para interfaz gráfica"


def check_psycopg2():
    """Verifica instalación de psycopg2"""
    try:
        import psycopg2
        version = psycopg2.__version__
        return True, f"psycopg2 {version} instalado"
    except ImportError:
        return False, "psycopg2 no está instalado - Requerido para conexión a PostgreSQL"


def check_pyodbc():
    """Verifica instalación de pyodbc"""
    try:
        import pyodbc
        version = pyodbc.version
        return True, f"pyodbc {version} instalado"
    except ImportError:
        return False, "pyodbc no está instalado - Requerido para importar desde Access"


def check_access_driver():
    """Verifica driver ODBC de Microsoft Access"""
    try:
        import pyodbc
        drivers = [d for d in pyodbc.drivers() if 'Access' in d or 'accdb' in d.lower()]
        
        if drivers:
            driver_list = ', '.join(drivers)
            return True, f"Driver(s) ODBC de Access encontrado(s): {driver_list}"
        else:
            return False, (
                "No se encontró driver ODBC de Microsoft Access.\n"
                "   Descargue: Microsoft Access Database Engine 2016 Redistributable\n"
                "   Link: https://www.microsoft.com/en-us/download/details.aspx?id=54920"
            )
    except ImportError:
        return False, "pyodbc no instalado - No se puede verificar driver de Access"
    except Exception as e:
        return False, f"Error verificando driver: {str(e)}"


def check_qgis_available():
    """Verifica si QGIS está disponible"""
    try:
        from qgis.core import Qgis
        version = Qgis.QGIS_VERSION
        return True, f"QGIS {version} detectado"
    except ImportError:
        return False, "QGIS no detectado - Este script se ejecuta mejor desde QGIS Python Console"


def check_postgresql_connection():
    """Intenta verificar conexión a PostgreSQL usando configuración guardada"""
    try:
        import json
        import os
        
        # Buscar archivo de configuración
        config_paths = [
            'db_config.json',
            '../db_config.json',
            '../../db_config.json',
        ]
        
        config = None
        for path in config_paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    config = json.load(f)
                break
        
        if not config:
            return False, "No se encontró configuración de BD (db_config.json)"
        
        # Intentar conectar
        import psycopg2
        conn = psycopg2.connect(
            host=config.get('host', 'localhost'),
            port=config.get('port', 5432),
            user=config.get('user', ''),
            password=config.get('password', ''),
            dbname=config.get('dbname', ''),
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        # Verificar PostGIS
        cursor.execute("SELECT PostGIS_version();")
        postgis_version = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return True, f"Conexión exitosa a PostgreSQL con PostGIS {postgis_version}"
    
    except psycopg2.OperationalError as e:
        return False, f"No se pudo conectar a PostgreSQL: {str(e)}"
    except Exception as e:
        return False, f"Error verificando PostgreSQL: {str(e)}"


def check_disk_space():
    """Verifica espacio disponible en disco"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        
        free_mb = free // (1024 * 1024)
        free_gb = free_mb / 1024
        
        if free_mb >= 500:
            return True, f"Espacio libre: {free_gb:.2f} GB (suficiente)"
        else:
            return False, f"Espacio libre: {free_gb:.2f} GB - Se recomienda al menos 500 MB"
    except Exception as e:
        return False, f"No se pudo verificar espacio en disco: {str(e)}"


def check_internet_connection():
    """Verifica conexión a Internet (opcional)"""
    try:
        import urllib.request
        urllib.request.urlopen('https://www.google.com', timeout=5)
        return True, "Conexión a Internet disponible (para geocodificación y mapas base)"
    except:
        return False, "Sin conexión a Internet - Funcionalidad de geocodificación no disponible"


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Ejecuta todas las verificaciones"""
    checker = DependencyChecker()
    
    print("\nIniciando verificación de dependencias...\n")
    
    # Verificaciones críticas
    checker.check("Python 3.7+", check_python_version, critical=True)
    checker.check("Sistema Operativo", check_operating_system, critical=False)
    checker.check("PyQt5", check_pyqt5, critical=True)
    checker.check("psycopg2", check_psycopg2, critical=True)
    checker.check("pyodbc", check_pyodbc, critical=True)
    checker.check("Driver ODBC Access", check_access_driver, critical=True)
    checker.check("QGIS", check_qgis_available, critical=False)
    checker.check("Conexión PostgreSQL", check_postgresql_connection, critical=True)
    checker.check("Espacio en Disco", check_disk_space, critical=False)
    checker.check("Conexión a Internet", check_internet_connection, critical=False)
    
    # Imprimir resultados
    checker.print_results()
    
    # Guardar reporte
    checker.save_report()
    
    # Retornar código de salida
    return 0 if not checker.errors else 1


if __name__ == "__main__":
    sys.exit(main())
