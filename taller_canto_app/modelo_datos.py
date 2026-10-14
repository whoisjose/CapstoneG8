"""
Modelo de datos - Plataforma de Gestion para Talleres de Canto Independientes
Entidades de este avance: Alumno, Clase, Asistencia.
(Progreso/objetivos y Evaluaciones se agregan en la siguiente etapa del plan.)

La base es SQLite: un archivo (taller_canto.db) que se crea solo, sin instalar nada.
"""
import os
import sqlite3

# La base queda siempre junto a este archivo, sin importar desde donde se ejecute
DB_PATH = os.environ.get(
    "TALLER_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "taller_canto.db"),
)


def crear_base_de_datos():
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    # ALUMNO: la ficha individual de cada estudiante
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alumno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            fecha_ingreso TEXT
        )
    """)

    # CLASE: cada sesion del taller
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clase (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            tema TEXT
        )
    """)

    # ASISTENCIA: relaciona alumno y clase (quien vino a que clase)
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


if __name__ == "__main__":
    crear_base_de_datos()
    print("Base de datos lista en:", DB_PATH)
