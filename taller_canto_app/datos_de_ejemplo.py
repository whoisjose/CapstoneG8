"""Carga alumnos y clases de EJEMPLO (ficticios) para tener algo que mostrar en el demo.
Solo carga si la base esta vacia. Ejecutar:  python datos_de_ejemplo.py"""
import sqlite3
from modelo_datos import crear_base_de_datos, DB_PATH

crear_base_de_datos()
con = sqlite3.connect(DB_PATH)
if con.execute("SELECT COUNT(*) FROM alumno").fetchone()[0] > 0:
    print("La base ya tiene alumnos; no se cargo nada.")
else:
    alumnos = [("Camila Rojas", "camila@correo.cl", "2026-03-10"),
               ("Matias Fuentes", "+56 9 1111 2222", "2026-03-10"),
               ("Javiera Soto", "javiera@correo.cl", "2026-04-02"),
               ("Benjamin Araya", "+56 9 3333 4444", "2026-05-15")]
    for a in alumnos:
        con.execute("INSERT INTO alumno (nombre, contacto, fecha_ingreso) VALUES (?, ?, ?)", a)
    clases = [("2026-09-02", "Tecnica de respiracion"), ("2026-09-09", "Afinacion y calentamiento")]
    asist = {1: [1, 1, 1, 0], 2: [1, 0, 1, 1]}  # clase_id -> presente de cada alumno
    for i, c in enumerate(clases, start=1):
        con.execute("INSERT INTO clase (fecha, tema) VALUES (?, ?)", c)
        for alumno_id, p in enumerate(asist[i], start=1):
            con.execute("INSERT INTO asistencia (alumno_id, clase_id, presente) VALUES (?, ?, ?)", (alumno_id, i, p))
    con.commit()
    print("Datos de ejemplo cargados.")
con.close()
