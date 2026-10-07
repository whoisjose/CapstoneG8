"""
Modelo de datos — Plataforma de Gestión para Talleres de Canto Independientes
Entidades: Alumno, Clase, Asistencia (progreso y evaluaciones se agregan en la siguiente fase)

Este archivo crea la base de datos SQLite y las tablas. Se ejecuta una sola vez
(o cada vez que quieras reiniciar los datos de prueba).
"""
import sqlite3

DB_PATH = "taller_canto.db"


def crear_base_de_datos():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # Entidad Alumno: la "ficha individual" de cada estudiante del taller
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            fecha_ingreso TEXT
        )
    """)

    # Entidad Clase: cada sesión de taller que se dicta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tema TEXT
        )
    """)

    # Entidad Asistencia: relación entre alumno y clase (quién vino a qué clase)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumno_id INTEGER NOT NULL,
            clase_id INTEGER NOT NULL,
            presente INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (alumno_id) REFERENCES alumno(id),
            FOREIGN KEY (clase_id) REFERENCES clase(id)
        )
    """)

    conexion.commit()
    conexion.close()
    print(f"Base de datos creada/verificada en {DB_PATH}")


if __name__ == "__main__":
    crear_base_de_datos()
