import tkinter as tk
from tkinter import messagebox, ttk
from DataBase import conectar
import re

def createTeacherWindow():
    def agregar_maestro():
        conn = conectar()
        cursor = conn.cursor()

        id_maestro = idEntry.get()
        nombre = nameEntry.get()
        a_paterno = midName.get()
        a_materno = lasName.get()
        correo = emailEntry.get()
        carrera = carreraEntry.get()  # Nombre de la carrera seleccionada en la interfaz
        materias_seleccionadas = [materiaListbox.get(i) for i in materiaListbox.curselection()]
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (
                id_maestro and nombre and a_paterno and a_materno and correo and carrera and materias_seleccionadas and grado):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación de formato de correo electrónico
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, correo):
            messagebox.showinfo("Error", "El correo electrónico no tiene un formato válido")
            return

        try:
            # Insertar en la tabla Maestros
            cursor.execute(
                "INSERT INTO Maestros (id_maestro, nombre, a_paterno, a_materno, correo, grado_estudio) VALUES (?, ?, ?, ?, ?, ?)",
                (id_maestro, nombre, a_paterno, a_materno, correo, grado))
            conn.commit()

            # Obtener el ID de la carrera basada en el nombre
            cursor.execute("SELECT id_carrera FROM Carreras WHERE nombre_carrera = ?", (carrera,))
            resultado_carrera = cursor.fetchone()

            if resultado_carrera is None:
                messagebox.showinfo("Error", "La carrera seleccionada no existe en la base de datos")
                return

            id_carrera = resultado_carrera[0]  # ID de la carrera

            # Insertar en la tabla Maestro_Carreras con las llaves primarias
            cursor.execute(
                "INSERT INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)",
                (id_maestro, id_carrera))
            conn.commit()

            # Insertar en la tabla Maestro_Materias para cada materia seleccionada
            for materia in materias_seleccionadas:
                cursor.execute("SELECT id_materia FROM Materias WHERE nombre_materia = ?", (materia,))
                resultado_materia = cursor.fetchone()

                if resultado_materia is None:
                    messagebox.showinfo("Error", f"La materia '{materia}' no existe en la base de datos")
                    continue

                id_materia = resultado_materia[0]  # ID de la materia

                cursor.execute(
                    "INSERT INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)",
                    (id_maestro, id_materia))
                conn.commit()

            messagebox.showinfo("Éxito", "Maestro, materias y carrera registrados correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def buscar_profesor():
        conn = conectar()
        cursor = conn.cursor()

        id_maestro = idSearch.get()  # Obtenemos el ID del maestro desde la interfaz

        if not id_maestro:
            messagebox.showinfo("Error", "Por favor ingrese un ID de maestro")
            return

        try:
            # Consultar los detalles del maestro y su carrera desde la tabla Maestros
            cursor.execute(
                """
                SELECT m.nombre, m.a_paterno, m.a_materno, m.correo, m.grado_estudio, c.nombre_carrera
                FROM Maestros m
                JOIN Maestro_Carreras mc ON m.id_maestro = mc.id_maestro
                JOIN Carreras c ON mc.id_carrera = c.id_carrera
                WHERE m.id_maestro = ?
                """,
                (id_maestro,)
            )
            maestro = cursor.fetchone()

            if maestro:
                # Rellenar los campos con los datos del maestro obtenidos
                idEntry.delete(0, tk.END)
                idEntry.insert(tk.END, id_maestro)
                nameEntry.delete(0, tk.END)
                nameEntry.insert(tk.END, maestro[0])
                midName.delete(0, tk.END)
                midName.insert(tk.END, maestro[1])
                lasName.delete(0, tk.END)
                lasName.insert(tk.END, maestro[2])
                emailEntry.delete(0, tk.END)
                emailEntry.insert(tk.END, maestro[3])
                studyGrade.set(maestro[4])
                carreraEntry.set(maestro[5])

                # Consultar las materias asociadas al maestro desde la tabla Maestro_Materias
                cursor.execute(
                    """
                    SELECT ma.nombre_materia
                    FROM Materias ma
                    JOIN Maestro_Materias mm ON ma.id_materia = mm.id_materia
                    WHERE mm.id_maestro = ?
                    """,
                    (id_maestro,)
                )
                materias_asociadas = [row[0] for row in cursor.fetchall()]

                # Limpiar la lista de materias y seleccionar las asociadas
                materiaListbox.selection_clear(0, tk.END)
                for index in range(materiaListbox.size()):
                    materia = materiaListbox.get(index)
                    if materia in materias_asociadas:
                        materiaListbox.select_set(index)

                messagebox.showinfo("Maestro Encontrado",
                                    f"Maestro con ID '{id_maestro}' encontrado y campos llenados.")
            else:
                messagebox.showinfo("No Encontrado", "No se encontró un maestro con ese ID")

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def editar_maestro():
        conn = conectar()
        cursor = conn.cursor()

        id_maestro = idEntry.get()  # ID del maestro a editar
        nombre = nameEntry.get()
        a_paterno = midName.get()
        a_materno = lasName.get()
        correo = emailEntry.get()
        carrera = carreraEntry.get()  # Carrera seleccionada en la interfaz
        materias_seleccionadas = [materiaListbox.get(i) for i in materiaListbox.curselection()]
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (id_maestro and nombre and a_paterno and a_materno and correo and carrera and materias_seleccionadas and grado):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación de formato de correo electrónico
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, correo):
            messagebox.showinfo("Error", "El correo electrónico no tiene un formato válido")
            return

        try:
            # Actualizar datos en la tabla Maestros
            cursor.execute(
                "UPDATE Maestros SET nombre = ?, a_paterno = ?, a_materno = ?, correo = ?, grado_estudio = ? WHERE id_maestro = ?",
                (nombre, a_paterno, a_materno, correo, grado, id_maestro))
            conn.commit()

            # Obtener el ID de la carrera basada en el nombre
            cursor.execute("SELECT id_carrera FROM Carreras WHERE nombre_carrera = ?", (carrera,))
            resultado_carrera = cursor.fetchone()

            if resultado_carrera is None:
                messagebox.showinfo("Error", "La carrera seleccionada no existe en la base de datos")
                return

            id_carrera = resultado_carrera[0]  # ID de la carrera

            # Actualizar relación en la tabla Maestro_Carreras
            cursor.execute(
                "UPDATE Maestro_Carreras SET id_carrera = ? WHERE id_maestro = ?",
                (id_carrera, id_maestro))
            conn.commit()

            # Actualizar relación en la tabla Maestro_Materias para cada materia seleccionada
            cursor.execute("DELETE FROM Maestro_Materias WHERE id_maestro = ?", (id_maestro,))
            for materia in materias_seleccionadas:
                cursor.execute("SELECT id_materia FROM Materias WHERE nombre_materia = ?", (materia,))
                resultado_materia = cursor.fetchone()

                if resultado_materia is None:
                    messagebox.showinfo("Error", f"La materia '{materia}' no existe en la base de datos")
                    continue

                id_materia = resultado_materia[0]  # ID de la materia

                cursor.execute(
                    "INSERT INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)",
                    (id_maestro, id_materia))
                conn.commit()

            messagebox.showinfo("Éxito", "Datos del maestro, materias y carrera actualizados correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_profesor():
        conn = conectar()
        cursor = conn.cursor()
        id_maestro = idEntry.get()

        if not id_maestro:
            messagebox.showinfo("Error", "Por favor, busque un profesor para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación",
                                           "¿Estás seguro de que deseas eliminar este profesor y sus asociaciones?")
        if not confirmacion:
            return

        try:
            # Buscar los grupos asociados al maestro
            cursor.execute("SELECT id_grupo FROM Grupos WHERE id_maestro = ?", (id_maestro,))
            grupos = cursor.fetchall()

            for grupo in grupos:
                id_grupo = grupo[0]

                try:
                    conexion = conectar()
                    cursor = conexion.cursor()

                    # Eliminar registros relacionados en cascada
                    cursor.execute(
                        "DELETE FROM Alumnos_Grupos WHERE id_grupo IN (SELECT id_grupo FROM Grupos WHERE id_maestro = ?)",
                        (id_maestro,))
                    cursor.execute("DELETE FROM Grupos WHERE id_maestro = ?", (id_maestro,))
                    cursor.execute("DELETE FROM Profesores WHERE id_maestro = ?", (id_maestro,))

                    conexion.commit()
                    conexion.close()

                    messagebox.showinfo("Éxito","El profesor y sus registros relacionados fueron eliminados correctamente.")
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error al eliminar al profesor: {e}")
        finally:
            conn.close()

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        midName.delete(0, tk.END)
        lasName.delete(0, tk.END)
        emailEntry.delete(0, tk.END)
        carreraEntry.set('')
        materiaListbox.selection_clear(0, tk.END)
        studyGrade.set('')
        idSearch.delete(0, tk.END)

    # Configuración de la ventana principal
    teacherWindow = tk.Tk()
    teacherWindow.title("Gestión de Maestros")
    teacherWindow.geometry("600x600")

    # ID del maestro para búsquedas
    tk.Label(teacherWindow, text="ID de Maestro:").grid(row=0, column=0)
    idSearch = tk.Entry(teacherWindow)
    idSearch.grid(row=0, column=1)

    tk.Button(teacherWindow, text="Buscar", command=buscar_profesor).grid(row=0, column=2)

    # Información del maestro
    tk.Label(teacherWindow, text="ID del Maestro:").grid(row=1, column=0)
    idEntry = tk.Entry(teacherWindow)
    idEntry.grid(row=1, column=1)

    tk.Label(teacherWindow, text="Nombre:").grid(row=2, column=0)
    nameEntry = tk.Entry(teacherWindow)
    nameEntry.grid(row=2, column=1)

    tk.Label(teacherWindow, text="Apellido Paterno:").grid(row=3, column=0)
    midName = tk.Entry(teacherWindow)
    midName.grid(row=3, column=1)

    tk.Label(teacherWindow, text="Apellido Materno:").grid(row=4, column=0)
    lasName = tk.Entry(teacherWindow)
    lasName.grid(row=4, column=1)

    tk.Label(teacherWindow, text="Correo Electrónico:").grid(row=5, column=0)
    emailEntry = tk.Entry(teacherWindow)
    emailEntry.grid(row=5, column=1)

    tk.Label(teacherWindow, text="Carrera:").grid(row=6, column=0)
    carreraEntry = ttk.Combobox(teacherWindow)
    carreraEntry.grid(row=6, column=1)

    tk.Label(teacherWindow, text="Materias:").grid(row=7, column=0)
    materiaListbox = tk.Listbox(teacherWindow, selectmode=tk.MULTIPLE)
    materiaListbox.grid(row=7, column=1)

    tk.Label(teacherWindow, text="Grado de Estudios:").grid(row=8, column=0)
    studyGrade = ttk.Combobox(teacherWindow, values=["Licenciatura", "Maestría", "Doctorado"])
    studyGrade.grid(row=8, column=1)

    tk.Button(teacherWindow, text="Agregar Maestro", command=agregar_maestro).grid(row=9, column=0)
    tk.Button(teacherWindow, text="Editar Maestro", command=editar_maestro).grid(row=9, column=1)
    tk.Button(teacherWindow, text="Eliminar Maestro", command=eliminar_profesor).grid(row=9, column=2)
    tk.Button(teacherWindow, text="Limpiar Campos", command=limpiar_campos).grid(row=10, column=1)

    # Cargar las carreras en el Combobox al iniciar la ventana
    def cargar_carreras():
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre_carrera FROM Carreras")
            carreras = [row[0] for row in cursor.fetchall()]
            carreraEntry['values'] = carreras
        except Exception as e:
            messagebox.showinfo("Error al cargar carreras", str(e))
        finally:
            conn.close()

    # Cargar las materias en la Listbox al iniciar la ventana
    def cargar_materias():
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre_materia FROM Materias")
            materias = [row[0] for row in cursor.fetchall()]
            for materia in materias:
                materiaListbox.insert(tk.END, materia)
        except Exception as e:
            messagebox.showinfo("Error al cargar materias", str(e))
        finally:
            conn.close()

    cargar_carreras()
    cargar_materias()

    teacherWindow.mainloop()