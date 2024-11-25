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
        materia = materiaListbox.get()  # Materia seleccionada en la interfaz
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (id_maestro and nombre and a_paterno and a_materno and correo and carrera and materia and grado):
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

            # Obtener el ID de la materia basada en el nombre
            cursor.execute("SELECT id_materia FROM Materias WHERE nombre_materia = ?", (materia,))
            resultado_materia = cursor.fetchone()

            if resultado_materia is None:
                messagebox.showinfo("Error", "La materia seleccionada no existe en la base de datos")
                return

            id_materia = resultado_materia[0]  # ID de la materia

            # Actualizar relación en la tabla materias_maestros
            cursor.execute(
                "UPDATE Maestro_Materias SET id_materia = ? WHERE id_maestro = ?",
                (id_materia, id_maestro))
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

            messagebox.showinfo("Éxito", "Datos del maestro, materia y carrera actualizados correctamente")
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

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este profesor?")
        if not confirmacion:
            return

        try:
            cursor.execute("DELETE FROM Maestros WHERE id_maestro = ?", (id_maestro,))
            conn.commit()
            messagebox.showinfo("Éxito", "Profesor eliminado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        midName.delete(0, tk.END)
        lasName.delete(0, tk.END)
        emailEntry.delete(0, tk.END)
        materiaListbox.selection_clear(0, tk.END)
        carreraEntry.set("")
        studyGrade.set("")

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_maestro FROM Maestros ORDER BY id_maestro")
        ids_existentes = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Encontrar el primer ID faltante en la secuencia
        siguiente_id = 1
        for id_ in ids_existentes:
            if id_ == siguiente_id:
                siguiente_id += 1
            else:
                break
        # Mostrar el siguiente ID en el campo idEntry
        idEntry.delete(0, tk.END)
        idEntry.insert(0, siguiente_id)

    def obtener_datos_carrera_y_materia():
        conn = conectar()
        if conn is None:
            return [], []  # Retorna listas vacías si la conexión falla

        cursor = conn.cursor()

        # Obtener los datos de las tablas
        try:
            cursor.execute("SELECT nombre_carrera FROM Carreras")  # Consulta para la tabla de carreras
            carreras = [row[0] for row in cursor.fetchall()]

            cursor.execute("SELECT nombre_materia FROM Materias")  # Consulta para la tabla de materias
            materias = [row[0] for row in cursor.fetchall()]

            conn.close()
            return carreras, materias
        except Exception as e:
            print(f"Error en la consulta SQL: {e}")
            conn.close()
            return [], []  # Retorna listas vacías en caso de error en la consulta

    # Obtener los datos de ambas tablas
    carreras, materias = obtener_datos_carrera_y_materia()

    # Verificar si se obtuvieron datos
    if not carreras or not materias:
        print("No se pudieron cargar los datos para los comboboxes.")
        return

    # Crear la ventana
    teacherWindow = tk.Tk()
    teacherWindow.title("Maestros")
    teacherWindow.geometry("600x500")

    tk.Label(teacherWindow, text="Ingrese el ID a buscar").grid(row=0, column=0)
    idSearch = tk.Entry(teacherWindow)
    idSearch.grid(row=0, column=1)
    tk.Button(teacherWindow, text='Buscar', command=buscar_profesor).grid(row=0, column=2)

    tk.Label(teacherWindow, text="ID").grid(row=1, column=0)
    idEntry = tk.Entry(teacherWindow)  # Crear el widget
    idEntry.grid(row=1, column=1)  # Ubicar en la cuadrícula

    tk.Label(teacherWindow, text="Nombre").grid(row=2, column=0)
    nameEntry = tk.Entry(teacherWindow)
    nameEntry.grid(row=2, column=1)

    tk.Label(teacherWindow, text="A. Paterno").grid(row=3, column=0)
    midName = tk.Entry(teacherWindow)
    midName.grid(row=3, column=1)

    tk.Label(teacherWindow, text="A. Materno").grid(row=4, column=0)
    lasName = tk.Entry(teacherWindow)
    lasName.grid(row=4, column=1)

    tk.Label(teacherWindow, text="Email").grid(row=5, column=0)
    emailEntry = tk.Entry(teacherWindow)
    emailEntry.grid(row=5, column=1)

    # Crear los Combobox con los valores obtenidos de las tablas de la misma base de datos
    tk.Label(teacherWindow, text='Carrera').grid(row=1, column=3)
    carreraEntry = ttk.Combobox(teacherWindow, values=carreras)
    carreraEntry.grid(row=1, column=4)

    tk.Label(teacherWindow, text='Materias').grid(row=2, column=3)
    materiaListbox = tk.Listbox(teacherWindow, selectmode=tk.MULTIPLE, height=6)  # Cambiado a Listbox con selección múltiple
    for materia in materias:
        materiaListbox.insert(tk.END, materia)
    materiaListbox.grid(row=2, column=4)

    tk.Label(teacherWindow, text='Grado de estudios').grid(row=3, column=3)
    studyGrade = ttk.Combobox(teacherWindow, values=["Licenciatura", "Maestria", "Doctorado"])
    studyGrade.grid(row=3, column=4)

    # Botones de la ventana
    tk.Button(teacherWindow, text='Nuevo', command=obtener_siguiente_id).grid(row=6, column=0)
    tk.Button(teacherWindow, text='Guardar', command=agregar_maestro).grid(row=6, column=1)
    tk.Button(teacherWindow, text='Cancelar', command=limpiar_campos).grid(row=6, column=2)
    tk.Button(teacherWindow, text='Editar', command=editar_maestro).grid(row=6, column=3)
    tk.Button(teacherWindow, text='Baja', command=eliminar_profesor).grid(row=6, column=4)

    teacherWindow.mainloop()
