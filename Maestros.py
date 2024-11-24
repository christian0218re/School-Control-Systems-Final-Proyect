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
        materia = materiaEntry.get()  # Nombre de la materia seleccionada en la interfaz
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (
                id_maestro and nombre and a_paterno and a_materno and correo and carrera and materia and grado):
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

            # Obtener el ID de la materia basada en el nombre
            cursor.execute("SELECT id_materia FROM Materias WHERE nombre_materia = ?", (materia,))
            resultado_materia = cursor.fetchone()

            if resultado_materia is None:
                messagebox.showinfo("Error", "La materia seleccionada no existe en la base de datos")
                return

            id_materia = resultado_materia[0]  # ID de la materia

            # Insertar en la tabla Maestro_Materias con las llaves primarias
            cursor.execute(
                "INSERT INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)",
                (id_maestro, id_materia))
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

            messagebox.showinfo("Éxito", "Maestro, materia y carrera registrados correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def buscar_profesor():
        conn = conectar()
        cursor = conn.cursor()
        maestro_id = idSearch.get()

        if not maestro_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de usuario")
            return

        cursor.execute("SELECT * FROM Maestros WHERE id_maestro = ?", (maestro_id,))
        usuario = cursor.fetchone()

        if usuario:
            # Obtener la carrera y la materia asociada al maestro
            cursor.execute("""
                SELECT c.nombre_carrera, m.nombre_materia, maestros.grado_estudio
                FROM Maestro_Carreras mc
                JOIN Carreras c ON mc.id_carrera = c.id_carrera
                JOIN Maestro_Materias mm ON mc.id_maestro = mm.id_maestro
                JOIN Materias m ON mm.id_materia = m.id_materia
                JOIN Maestros maestros ON maestros.id_maestro = mc.id_maestro
                WHERE mc.id_maestro = ?
            """, (maestro_id,))

            resultado = cursor.fetchone()

            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, usuario[0])

            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, usuario[1])

            midName.delete(0, tk.END)
            midName.insert(tk.END, usuario[2])

            lasName.delete(0, tk.END)
            lasName.insert(tk.END, usuario[3])

            emailEntry.delete(0, tk.END)
            emailEntry.insert(tk.END, usuario[4])

            if resultado:
                carrera, materia, grado = resultado
                carreraEntry.set(carrera)
                materiaEntry.set(materia)
                studyGrade.set(grado)
            else:
                messagebox.showinfo("No Encontrado", "No se encontró carrera o materia asociada al maestro")

            messagebox.showinfo("Éxito", "Profesor encontrado y datos llenados")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un profesor con ese ID")

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
        materia = materiaEntry.get()  # Materia seleccionada en la interfaz
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
        materiaEntry.delete(0, tk.END)
        materiaEntry.set("")
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
    teacherWindow.geometry("600x450")

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

    tk.Label(teacherWindow, text='Materia').grid(row=2, column=3)
    materiaEntry = ttk.Combobox(teacherWindow, values=materias)
    materiaEntry.grid(row=2, column=4)

    tk.Label(teacherWindow, text='Grado de estudios').grid(row=3, column=3)
    studyGrade = ttk.Combobox(teacherWindow, values=["Licenciatura", "Maestria", "Doctorado"])
    studyGrade.grid(row=3, column=4)

    # Botones de la ventana
    tk.Button(teacherWindow, text='Nuevo', command=obtener_siguiente_id).grid(row = 6, column = 0)
    tk.Button(teacherWindow, text='Guardar', command=agregar_maestro).grid(row=6, column=1)
    tk.Button(teacherWindow, text='Cancelar', command=limpiar_campos).grid(row=6, column=2)
    tk.Button(teacherWindow, text='Editar', command=editar_maestro).grid(row=6, column=3)
    tk.Button(teacherWindow, text='Baja', command=eliminar_profesor).grid(row=6, column=4)

    teacherWindow.mainloop()