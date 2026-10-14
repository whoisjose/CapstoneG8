"""
Plataforma de Gestion para Talleres de Canto Independientes
Demo Fase 2 - Avance: modulo de Alumnos (CRUD) + modulo de Asistencia (registro y consulta)

Ejecutar:   python app.py
Abrir en:   http://127.0.0.1:5000
"""
import sqlite3
from flask import Flask, render_template, request, redirect, url_for
from modelo_datos import crear_base_de_datos, DB_PATH

app = Flask(__name__)


def obtener_conexion():
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row  # columnas accesibles por nombre
    return conexion


# ---------------- INICIO ----------------
@app.route("/")
def inicio():
    conexion = obtener_conexion()
    total_alumnos = conexion.execute("SELECT COUNT(*) FROM alumno").fetchone()[0]
    total_clases = conexion.execute("SELECT COUNT(*) FROM clase").fetchone()[0]
    conexion.close()
    return render_template("inicio.html", total_alumnos=total_alumnos, total_clases=total_clases)


# ---------------- MODULO ALUMNOS (CRUD) ----------------
@app.route("/alumnos")
def listar_alumnos():
    conexion = obtener_conexion()
    alumnos = conexion.execute("SELECT * FROM alumno ORDER BY nombre").fetchall()
    conexion.close()
    return render_template("alumnos.html", alumnos=alumnos)


@app.route("/alumnos/nuevo", methods=["GET", "POST"])
def nuevo_alumno():  # CREATE
    if request.method == "POST":
        conexion = obtener_conexion()
        conexion.execute(
            "INSERT INTO alumno (nombre, contacto, fecha_ingreso) VALUES (?, ?, ?)",
            (request.form["nombre"].strip(), request.form["contacto"].strip(), request.form["fecha_ingreso"]),
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("listar_alumnos"))
    return render_template("nuevo_alumno.html")


@app.route("/alumnos/<int:alumno_id>")
def ficha_alumno(alumno_id):  # READ (ficha individual + su historial de asistencia)
    conexion = obtener_conexion()
    alumno = conexion.execute("SELECT * FROM alumno WHERE id = ?", (alumno_id,)).fetchone()
    if alumno is None:
        conexion.close()
        return redirect(url_for("listar_alumnos"))
    asistencias = conexion.execute(
        """SELECT clase.fecha, clase.tema, asistencia.presente
           FROM asistencia
           JOIN clase ON asistencia.clase_id = clase.id
           WHERE asistencia.alumno_id = ?
           ORDER BY clase.fecha DESC""",
        (alumno_id,),
    ).fetchall()
    conexion.close()
    total = len(asistencias)
    presentes = sum(1 for a in asistencias if a["presente"])
    porcentaje = round(presentes * 100 / total) if total else None
    return render_template("ficha_alumno.html", alumno=alumno, asistencias=asistencias,
                           total=total, presentes=presentes, porcentaje=porcentaje)


@app.route("/alumnos/<int:alumno_id>/editar", methods=["GET", "POST"])
def editar_alumno(alumno_id):  # UPDATE
    conexion = obtener_conexion()
    if request.method == "POST":
        conexion.execute(
            "UPDATE alumno SET nombre = ?, contacto = ?, fecha_ingreso = ? WHERE id = ?",
            (request.form["nombre"].strip(), request.form["contacto"].strip(),
             request.form["fecha_ingreso"], alumno_id),
        )
        conexion.commit()
        conexion.close()
        return redirect(url_for("ficha_alumno", alumno_id=alumno_id))
    alumno = conexion.execute("SELECT * FROM alumno WHERE id = ?", (alumno_id,)).fetchone()
    conexion.close()
    if alumno is None:
        return redirect(url_for("listar_alumnos"))
    return render_template("editar_alumno.html", alumno=alumno)


@app.route("/alumnos/<int:alumno_id>/eliminar", methods=["POST"])
def eliminar_alumno(alumno_id):  # DELETE (primero borra su asistencia para no dejar datos huerfanos)
    conexion = obtener_conexion()
    conexion.execute("DELETE FROM asistencia WHERE alumno_id = ?", (alumno_id,))
    conexion.execute("DELETE FROM alumno WHERE id = ?", (alumno_id,))
    conexion.commit()
    conexion.close()
    return redirect(url_for("listar_alumnos"))


# ---------------- MODULO ASISTENCIA ----------------
@app.route("/asistencia", methods=["GET", "POST"])
def registrar_asistencia():
    conexion = obtener_conexion()
    if request.method == "POST":
        cursor = conexion.execute(
            "INSERT INTO clase (fecha, tema) VALUES (?, ?)",
            (request.form["fecha"], request.form["tema"].strip()),
        )
        clase_id = cursor.lastrowid
        for alumno in conexion.execute("SELECT id FROM alumno").fetchall():
            presente = 1 if request.form.get(f"presente_{alumno['id']}") else 0
            conexion.execute(
                "INSERT INTO asistencia (alumno_id, clase_id, presente) VALUES (?, ?, ?)",
                (alumno["id"], clase_id, presente),
            )
        conexion.commit()
        conexion.close()
        return redirect(url_for("detalle_clase", clase_id=clase_id))
    alumnos = conexion.execute("SELECT * FROM alumno ORDER BY nombre").fetchall()
    conexion.close()
    return render_template("registrar_asistencia.html", alumnos=alumnos)


@app.route("/clases")
def listar_clases():
    conexion = obtener_conexion()
    clases = conexion.execute(
        """SELECT clase.id, clase.fecha, clase.tema,
                  SUM(asistencia.presente) AS presentes, COUNT(asistencia.id) AS total
           FROM clase LEFT JOIN asistencia ON asistencia.clase_id = clase.id
           GROUP BY clase.id ORDER BY clase.fecha DESC, clase.id DESC"""
    ).fetchall()
    conexion.close()
    return render_template("clases.html", clases=clases)


@app.route("/clases/<int:clase_id>")
def detalle_clase(clase_id):  # consulta de asistencia POR CLASE
    conexion = obtener_conexion()
    clase = conexion.execute("SELECT * FROM clase WHERE id = ?", (clase_id,)).fetchone()
    if clase is None:
        conexion.close()
        return redirect(url_for("listar_clases"))
    registros = conexion.execute(
        """SELECT alumno.id, alumno.nombre, asistencia.presente
           FROM asistencia JOIN alumno ON asistencia.alumno_id = alumno.id
           WHERE asistencia.clase_id = ? ORDER BY alumno.nombre""",
        (clase_id,),
    ).fetchall()
    conexion.close()
    return render_template("detalle_clase.html", clase=clase, registros=registros)


if __name__ == "__main__":
    crear_base_de_datos()
    app.run(debug=False)
