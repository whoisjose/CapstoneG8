"""
Plataforma de Gestión para Talleres de Canto Independientes
Demo Fase 2 — Avance: módulo de Alumnos (completo) + módulo de Asistencia (nivel medio)

Para correrlo: python app.py
Luego abrir en el navegador: http://127.0.0.1:5000
"""
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from modelo_datos import crear_base_de_datos, DB_PATH

app = Flask(__name__)


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row  # permite acceder a columnas por nombre
    return conexion


# ---------- PÁGINA DE INICIO ----------
@app.route("/")
def inicio():
    return render_template("inicio.html")


# ---------- MÓDULO DE ALUMNOS ----------
@app.route("/alumnos")
def listar_alumnos():
    conexion = obtener_conexion()
    alumnos = conexion.execute("SELECT * FROM alumno ORDER BY nombre").fetchall()
    conexion.close()
    return render_template("alumnos.html", alumnos=alumnos)


@app.route("/alumnos/nuevo", methods=["GET", "POST"])
def nuevo_alumno():
    if request.method == "POST":
        nombre = request.form["nombre"]
        contacto = request.form["contacto"]
        fecha_ingreso = request.form["fecha_ingreso"]
        conexion = obtener_conexion()
        conexion.execute(
            "INSERT INTO alumno (nombre, contacto, fecha_ingreso) VALUES (?, ?, ?)",
            (nombre, contacto, fecha_ingreso),
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("listar_alumnos"))
    return render_template("nuevo_alumno.html")


@app.route("/alumnos/<int:alumno_id>")
def ficha_alumno(alumno_id):
    conexion = obtener_conexion()
    alumno = conexion.execute("SELECT * FROM alumno WHERE id = ?", (alumno_id,)).fetchone()
    # Consulta de asistencia de este alumno en particular (objetivo específico 3)
    asistencias = conexion.execute(
        """SELECT clase.fecha, clase.tema, asistencia.presente
           FROM asistencia
           JOIN clase ON asistencia.clase_id = clase.id
           WHERE asistencia.alumno_id = ?
           ORDER BY clase.fecha DESC""",
        (alumno_id,),
    ).fetchall()
    conexion.close()
    return render_template("ficha_alumno.html", alumno=alumno, asistencias=asistencias)


# ---------- MÓDULO DE ASISTENCIA (nivel medio, según plan de trabajo) ----------
@app.route("/asistencia", methods=["GET", "POST"])
def registrar_asistencia():
    conexion = obtener_conexion()

    if request.method == "POST":
        fecha = request.form["fecha"]
        tema = request.form["tema"]
        cursor = conexion.execute("INSERT INTO clase (fecha, tema) VALUES (?, ?)", (fecha, tema))
        clase_id = cursor.lastrowid

        alumnos = conexion.execute("SELECT id FROM alumno").fetchall()
        for alumno in alumnos:
            presente = 1 if request.form.get(f"presente_{alumno['id']}") else 0
            conexion.execute(
                "INSERT INTO asistencia (alumno_id, clase_id, presente) VALUES (?, ?, ?)",
                (alumno["id"], clase_id, presente),
            )
        conexion.commit()
        conexion.close()
        return redirect(url_for("listar_clases"))

    alumnos = conexion.execute("SELECT * FROM alumno ORDER BY nombre").fetchall()
    conexion.close()
    return render_template("registrar_asistencia.html", alumnos=alumnos)


@app.route("/clases")
def listar_clases():
    conexion = obtener_conexion()
    clases = conexion.execute("SELECT * FROM clase ORDER BY fecha DESC").fetchall()
    conexion.close()
    return render_template("clases.html", clases=clases)


if __name__ == "__main__":
    crear_base_de_datos()  # se asegura de que la base exista antes de arrancar
    app.run(debug=True)
