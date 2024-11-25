import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from DataBase import conectar
import re

studentWindow = None

def createStudentWindow(idUsuario, rol):
    id_usuario = idUsuario

    def procesarAlumno(id_usuario):
        if validarRolAlumno(id_usuario):
            if validarAlumno(id_usuario):
                agregar_CuentaAlumno(id_usuario)
                buscar_alumno(id_usuario)
            else:
                buscar_alumno(id_usuario)

    def agregar_estudiante():
        conn = conectar()
        cursor = conn.cursor()

        id_estudiante = idEntry.get()
        nombre = nameEntry.get()
        a_paterno = midNameEntry.get()
        a_materno = lasNameEntry.get()
        email = emailEntry.get()
        estado = stateEntry.get()
        fechaNac = birthEntry.get()
        carrera = careerEntry.get()

        # Verificar que todos los campos están completos
        if not (id_estudiante and nombre and a_paterno and a_materno and email and estado and fechaNac and carrera):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación del formato de correo electrónico
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            messagebox.showinfo("Error", "El correo electrónico no es válido")
            return

        # Verificar que el correo no esté ya registrado
        cursor.execute("SELECT * FROM Alumnos WHERE correo = ?", (email,))
        if cursor.fetchone():
            messagebox.showinfo("Error", "El correo electrónico ya está registrado")
            return

        # Intentar agregar el estudiante
        try:
            cursor.execute(
                "INSERT INTO Alumnos (id_alumno, nombre, fecha_nacimiento, A_paterno, A_materno, carrera, estado, correo, id_usuario) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (id_estudiante, nombre, fechaNac, a_paterno, a_materno, carrera, estado, email, id_usuario)
                # Aseguramos que id_usuario se inserte
            )
            conn.commit()

            # Obtener el ID del alumno recién agregado
            cursor.execute("SELECT id_alumno FROM Alumnos WHERE correo = ?", (email,))
            id_alumno = cursor.fetchone()[0]

            # Agregar las materias seleccionadas a la tabla Alumno_Materias
            materias_seleccionadas = materiaListbox.curselection()
            for index in materias_seleccionadas:
                id_materia = index + 1  # Suponiendo que los IDs de materias son índices + 1
                cursor.execute(
                    "INSERT INTO Alumno_Materias (id_alumno, id_materia) VALUES (?, ?)",
                    (id_alumno, id_materia)
                )
            conn.commit()

            messagebox.showinfo("Éxito", "Alumno registrado correctamente y materias agregadas")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def buscar_estudiante():
        conn = conectar()
        cursor = conn.cursor()
        estudiante_id = idEntryBusqueda.get()

        if not estudiante_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de estudiante")
            return

        cursor.execute("SELECT * FROM Alumnos WHERE id_alumno = ?", (estudiante_id,))
        alumno = cursor.fetchone()

        if alumno:
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, alumno[0])
            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, alumno[1])
            birthEntry.set_date(alumno[2])
            midNameEntry.delete(0, tk.END)
            midNameEntry.insert(tk.END, alumno[3])
            lasNameEntry.delete(0, tk.END)
            lasNameEntry.insert(tk.END, alumno[4])
            careerEntry.set(alumno[5])
            stateEntry.delete(0, tk.END)
            stateEntry.insert(tk.END, alumno[6])
            emailEntry.delete(0, tk.END)
            emailEntry.insert(tk.END, alumno[7])

            # Limpiar el Listbox antes de agregar las materias
            materiaListbox.selection_clear(0, tk.END)

            # Obtener las materias asociadas al alumno
            cursor.execute("""
                SELECT M.nombre_materia FROM Materias M
                JOIN Alumno_Materias AM ON AM.id_materia = M.id_materia
                WHERE AM.id_alumno = ?
            """, (estudiante_id,))
            materias_alumno = cursor.fetchall()

            # Marcar las materias seleccionadas en el Listbox
            for materia in materias_alumno:
                materia_nombre = materia[0]
                index = materiaListbox.get(0, tk.END).index(materia_nombre)
                materiaListbox.selection_set(index)

            messagebox.showinfo("Éxito", "Alumno encontrado y datos llenados")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un alumno con ese ID")

        conn.close()

    def editar_estudiante():
        conn = conectar()
        cursor = conn.cursor()

        id_estudiante = idEntry.get()
        nombre = nameEntry.get()
        a_paterno = midNameEntry.get()
        a_materno = lasNameEntry.get()
        email = emailEntry.get()
        estado = stateEntry.get()
        fechaNac = birthEntry.get()
        carrera = careerEntry.get()

        if not (id_estudiante and nombre and a_paterno and a_materno and email and estado and fechaNac and carrera):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación del formato de correo electrónico
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            messagebox.showinfo("Error", "El correo electrónico no es válido")
            return

        # Verificar que el correo no esté ya registrado (excluyendo el correo del estudiante actual)
        cursor.execute("SELECT * FROM Alumnos WHERE correo = ? AND id_alumno != ?", (email, id_estudiante))
        if cursor.fetchone():
            messagebox.showinfo("Error", "El correo electrónico ya está registrado")
            return

        try:
            cursor.execute(
                "UPDATE Alumnos SET nombre = ?, fecha_nacimiento = ?, A_paterno = ?, A_materno = ?, carrera = ?, estado = ?, correo = ? WHERE id_alumno = ?",
                (nombre, fechaNac, a_paterno, a_materno, carrera, estado, email, id_estudiante))
            conn.commit()

            # Limpiar las materias existentes en Alumno_Materias
            cursor.execute("DELETE FROM Alumno_Materias WHERE id_alumno = ?", (id_estudiante,))
            conn.commit()

            # Agregar las nuevas materias seleccionadas a la tabla Alumno_Materias
            materias_seleccionadas = materiaListbox.curselection()
            for index in materias_seleccionadas:
                id_materia = index + 1  # Suponiendo que los IDs de materias son índices + 1
                cursor.execute(
                    "INSERT INTO Alumno_Materias (id_alumno, id_materia) VALUES (?, ?)",
                    (id_estudiante, id_materia)
                )
            conn.commit()

            messagebox.showinfo("Éxito", "Alumno actualizado correctamente y materias actualizadas")
            if (rol != "alumno"):
                limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_estudiante():
        conn = conectar()
        cursor = conn.cursor()
        id_estudiante = idEntry.get()

        if not id_estudiante:
            messagebox.showinfo("Error", "Por favor, busque un alumno para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este estudiante?")
        if not confirmacion:
            return

        try:
            # Eliminar las materias asociadas al alumno
            cursor.execute("DELETE FROM Alumno_Materias WHERE id_alumno = ?", (id_estudiante,))
            conn.commit()

            cursor.execute("DELETE FROM Alumnos WHERE id_alumno = ?", (id_estudiante,))
            conn.commit()
            messagebox.showinfo("Éxito", "Alumno eliminado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        midNameEntry.delete(0, tk.END)
        lasNameEntry.delete(0, tk.END)
        emailEntry.delete(0, tk.END)
        stateEntry.delete(0, tk.END)
        birthEntry.set_date("2000-01-01")
        careerEntry.set("")
        materiaListbox.selection_clear(0, tk.END)  # Limpiar selección del Listbox

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_alumno FROM Alumnos ORDER BY id_alumno")
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

    def obtener_datos(query):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(query)
        data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data

    # Creación de la interfaz gráfica
    global studentWindow
    studentWindow = tk.Toplevel()
    studentWindow.title("Gestión de Estudiantes")

    # Fila de búsqueda por ID de estudiante
    labelBusqueda = tk.Label(studentWindow, text="Buscar por ID de Estudiante:")
    labelBusqueda.grid(row=0, column=0, padx=10, pady=10)

    idEntryBusqueda = tk.Entry(studentWindow)
    idEntryBusqueda.grid(row=0, column=1, padx=10, pady=10)

    buscarButton = tk.Button(studentWindow, text="Buscar", command=buscar_estudiante)
    buscarButton.grid(row=0, column=2, padx=10, pady=10)

    # Labels y Entradas para los campos
    tk.Label(studentWindow, text="ID Estudiante:").grid(row=1, column=0, padx=10, pady=10)
    idEntry = tk.Entry(studentWindow)
    idEntry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Nombre:").grid(row=2, column=0, padx=10, pady=10)
    nameEntry = tk.Entry(studentWindow)
    nameEntry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Apellido Paterno:").grid(row=3, column=0, padx=10, pady=10)
    midNameEntry = tk.Entry(studentWindow)
    midNameEntry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Apellido Materno:").grid(row=4, column=0, padx=10, pady=10)
    lasNameEntry = tk.Entry(studentWindow)
    lasNameEntry.grid(row=4, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Correo:").grid(row=5, column=0, padx=10, pady=10)
    emailEntry = tk.Entry(studentWindow)
    emailEntry.grid(row=5, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Estado:").grid(row=6, column=0, padx=10, pady=10)
    stateEntry = tk.Entry(studentWindow)
    stateEntry.grid(row=6, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Fecha de Nacimiento:").grid(row=7, column=0, padx=10, pady=10)
    birthEntry = DateEntry(studentWindow, date_pattern='yyyy-mm-dd')
    birthEntry.grid(row=7, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Carrera:").grid(row=8, column=0, padx=10, pady=10)
    careerEntry = ttk.Combobox(studentWindow)
    careerEntry.grid(row=8, column=1, padx=10, pady=10)

    tk.Label(studentWindow, text="Materias:").grid(row=9, column=0, padx=10, pady=10)
    materiaListbox = tk.Listbox(studentWindow, selectmode=tk.MULTIPLE)
    materiaListbox.grid(row=9, column=1, padx=10, pady=10)

    # Cargar las carreras y materias desde la base de datos
    careerList = obtener_datos("SELECT nombre_carrera FROM Carreras")
    careerEntry['values'] = careerList

    materiaList = obtener_datos("SELECT nombre_materia FROM Materias")
    for materia in materiaList:
        materiaListbox.insert(tk.END, materia)

    # Botones de acción
    agregarButton = tk.Button(studentWindow, text="Agregar Estudiante", command=agregar_estudiante)
    agregarButton.grid(row=10, column=0, padx=10, pady=10)

    editarButton = tk.Button(studentWindow, text="Editar Estudiante", command=editar_estudiante)
    editarButton.grid(row=10, column=1, padx=10, pady=10)

    nuevoBoton = tk.Button(studentWindow, text="Nuevo", command=obtener_siguiente_id)
    nuevoBoton.grid(row=10, column=2, padx=10, pady=10)

    eliminarButton = tk.Button(studentWindow, text="Eliminar Estudiante", command=eliminar_estudiante)
    eliminarButton.grid(row=10, column=3, padx=10, pady=10)

    limpiarButton = tk.Button(studentWindow, text="Limpiar Campos", command=limpiar_campos)
    limpiarButton.grid(row=11, column=0, padx=10, pady=10)

    studentWindow.mainloop()

    studentWindow.geometry("600x400")

    def validarRolAlumno(id_usuario):
        conn = conectar()
        cursor = conn.cursor()
        try:
            # Validar que el id_usuario es del tipo alumno en Usuarios
            cursor.execute("SELECT tipo_usuario FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
            resultado = cursor.fetchone()
            if not resultado or resultado[0] != 'alumno':
                return False

        except Exception as e:
            messagebox.showinfo("Error", f"Error al validar: {str(e)}")
            return False

        finally:
            conn.close()

        return True

    def validarAlumno(id_usuario):
        conn = conectar()
        cursor = conn.cursor()

        try:
            # Validar que el id_usuario es del tipo alumno en Usuarios
            cursor.execute("SELECT tipo_usuario FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
            resultado = cursor.fetchone()
            if not resultado or resultado[0] != 'alumno':
                return False

            # Validar que el id_usuario ya tiene un registro en Alumnos
            cursor.execute("SELECT * FROM Alumnos WHERE id_usuario = ?", (id_usuario,))
            alumno = cursor.fetchone()
            if alumno:
                return False


        except Exception as e:
            messagebox.showinfo("Error", f"Error al validar: {str(e)}")
            return False

        finally:
            conn.close()
        return True;

    def buscar_alumno(id_usuario):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Alumnos WHERE id_usuario = ?", (id_usuario,))
        alumno = cursor.fetchone()

        if alumno:
            if (alumno[6] == None):
                idEntry.insert(tk.END, alumno[0])
                nameEntry.insert(tk.END, alumno[1])
                birthEntry.set_date(alumno[2])
                midNameEntry.insert(tk.END, alumno[3])
                lasNameEntry.insert(tk.END, alumno[4])
                emailEntry.insert(tk.END, alumno[7])
                messagebox.showinfo("Éxito", "Alumno encontrado")
            else:
                idEntry.delete(0, tk.END)
                idEntry.insert(tk.END, alumno[0])
                nameEntry.delete(0, tk.END)
                nameEntry.insert(tk.END, alumno[1])
                birthEntry.set_date(alumno[2])
                midNameEntry.delete(0, tk.END)
                midNameEntry.insert(tk.END, alumno[3])
                lasNameEntry.delete(0, tk.END)
                lasNameEntry.insert(tk.END, alumno[4])
                careerEntry.set(alumno[5])
                stateEntry.delete(0, tk.END)
                stateEntry.insert(tk.END, alumno[6])
                emailEntry.delete(0, tk.END)
                emailEntry.insert(tk.END, alumno[7])
                messagebox.showinfo("Éxito", "Alumno encontrado")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un alumno con ese ID")

        conn.close()

    def agregar_CuentaAlumno(id_usuario):
        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT nombre, a_paterno, a_materno, correo FROM Usuarios WHERE id_usuario = ?",
                (id_usuario,)
            )
            usuario = cursor.fetchone()

            if not usuario:
                messagebox.showinfo("Error", "El usuario no existe.")
                return

            nombre, a_paterno, a_materno, correo = usuario

            cursor.execute("SELECT * FROM Alumnos WHERE correo = ?", (correo,))
            if cursor.fetchone():
                messagebox.showinfo("Error", "El correo ya está registrado como alumno.")
                return

            cursor.execute("SELECT id_alumno FROM Alumnos ORDER BY id_alumno")
            ids_existentes = [row[0] for row in cursor.fetchall()]

            siguiente_id = 1
            for id_ in ids_existentes:
                if id_ == siguiente_id:
                    siguiente_id += 1

            cursor.execute(
                "INSERT INTO Alumnos (id_alumno,nombre, a_paterno, a_materno, correo, id_usuario) VALUES (?,?, ?, ?, ?,?)",
                (siguiente_id, nombre, a_paterno, a_materno, correo, id_usuario)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Alumno registrado correctamente.")
        except Exception as e:
            messagebox.showinfo("Error", f"No se pudo registrar al alumno: {str(e)}")
        finally:
            conn.close()

    procesarAlumno(id_usuario)
    studentWindow.mainloop()