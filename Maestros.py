import tkinter as tk
from tkinter import messagebox, ttk
from DataBase import conectar
import re

def createTeacherWindow(idUsuario,rol):
    id_usuario = idUsuario
    def procesarMaestro(id_usuario):
        if validarRolMaestro(id_usuario):
            if validarMaestro(id_usuario):
                agregar_cuentaMaestro(id_usuario)
                buscar_maestro(id_usuario)
            else:
                buscar_maestro(id_usuario)

    def agregar_maestro():
        conn = conectar()
        cursor = conn.cursor()

        id_maestro = idEntry.get()
        nombre = nameEntry.get()
        a_paterno = midName.get()
        a_materno = lasName.get()
        correo = emailEntry.get()
        carreras_seleccionadas = [carreraListbox.get(i) for i in carreraListbox.curselection()]
        materias_seleccionadas = [materiaListbox.get(i) for i in materiaListbox.curselection()]
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (
                id_maestro and nombre and a_paterno and a_materno and correo and carreras_seleccionadas and materias_seleccionadas and grado):
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

            # Obtener el ID de las carreras seleccionadas
            for carrera in carreras_seleccionadas:
                cursor.execute("SELECT id_carrera FROM Carreras WHERE nombre_carrera = ?", (carrera,))
                resultado_carrera = cursor.fetchone()

                if resultado_carrera is None:
                    messagebox.showinfo('Error', f'La carrera {carrera} no existe en la base de datos')
                    continue

                id_carrera = resultado_carrera[0]
                cursor.execute(
                    "INSERT INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)",
                    (id_maestro, id_carrera))

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

        id_maestro = idSearch.get()

        if not id_maestro:
            messagebox.showinfo("Error", "Por favor ingrese un ID de maestro")
            return

        try:
            # Consultar los detalles del maestro
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

                # Consultar las materias asociadas al maestro
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

                cursor.execute(
                    """
                    SELECT ca.nombre_carrera
                    FROM Carreras ca
                    JOIN Maestro_Carreras mm ON ca.id_carrera = mm.id_carrera
                    WHERE mm.id_maestro = ?
                    """,
                    (id_maestro,)
                )
                carreras_asociadas = [row[0] for row in cursor.fetchall()]
                carreraListbox.selection_clear(0, tk.END)
                for index in range(carreraListbox.size()):
                    carrera = carreraListbox.get(index)
                    if carrera in carreras_asociadas:
                        carreraListbox.select_set(index)

                messagebox.showinfo("Maestro Encontrado",
                                    f"Maestro con ID '{id_maestro}' encontrado y campos llenados.")
            else:
                messagebox.showinfo("No Encontrado", "No se encontró un maestro con ese ID")

        except Exception as e:
            messagebox.showinfo("Error", str(e))

    def editar_maestro():
        conn = conectar()
        cursor = conn.cursor()

        id_maestro = idEntry.get()  # ID del maestro a editar
        nombre = nameEntry.get()
        a_paterno = midName.get()
        a_materno = lasName.get()
        correo = emailEntry.get()
        carreras_seleccionadas = [carreraListbox.get(i) for i in carreraListbox.curselection()]
        materias_seleccionadas = [materiaListbox.get(i) for i in materiaListbox.curselection()]
        grado = studyGrade.get()

        # Validación de campos vacíos
        if not (id_maestro and nombre and a_paterno and a_materno and correo and carreras_seleccionadas and materias_seleccionadas and grado):
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

            # Actualizar relación en la tabla Maestro_Carreras
            cursor.execute("DELETE FROM Maestro_Carreras WHERE id_maestro = ?", (id_maestro,))
            for carrera in carreras_seleccionadas:
                cursor.execute("SELECT id_carrera FROM Carreras WHERE nombre_carrera = ?", (carrera,))
                resultado_carrera = cursor.fetchone()

                if resultado_carrera is None:
                    messagebox.showinfo("Error", f"La carrera '{carrera}' no existe en la base de datos")
                    continue

                id_carrera = resultado_carrera[0]  # ID de la carrera

                cursor.execute(
                    "INSERT INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)",
                    (id_maestro, id_carrera))
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

            messagebox.showinfo("Éxito", "Datos del maestro actualizados correctamente")
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
            # Iniciar una transacción
            conn.begin()

            # Buscar las materias y carreras asociadas al maestro
            cursor.execute("SELECT id_materia FROM Maestro_Materias WHERE id_maestro = ?", (id_maestro,))
            materias = cursor.fetchall()

            cursor.execute("SELECT id_carrera FROM Maestro_Carreras WHERE id_maestro = ?", (id_maestro,))
            carreras = cursor.fetchall()

            # Eliminar las relaciones en Maestro_Materias y Maestro_Carreras
            for materia in materias:
                cursor.execute("DELETE FROM Maestro_Materias WHERE id_maestro = ? AND id_materia = ?",
                               (id_maestro, materia[0]))

            for carrera in carreras:
                cursor.execute("DELETE FROM Maestro_Carreras WHERE id_maestro = ? AND id_carrera = ?",
                               (id_maestro, carrera[0]))

            # Eliminar las relaciones de los grupos asociados al maestro
            cursor.execute("SELECT id_grupo FROM Grupos WHERE id_maestro = ?", (id_maestro,))
            grupos = cursor.fetchall()

            for grupo in grupos:
                id_grupo = grupo[0]
                try:
                    # Eliminar registros relacionados en cascada
                    cursor.execute("DELETE FROM Alumnos_Grupos WHERE id_grupo = ?", (id_grupo,))
                    cursor.execute("DELETE FROM Grupos WHERE id_grupo = ?", (id_grupo,))
                except Exception as e:
                    messagebox.showerror("Error", f"Ocurrió un error al eliminar los grupos: {e}")
                    conn.rollback()  # Revertir la transacción en caso de error
                    return

            # Eliminar al maestro
            cursor.execute("DELETE FROM Maestros WHERE id_maestro = ?", (id_maestro,))

            # Confirmar la transacción
            conn.commit()

            messagebox.showinfo("Éxito", "El profesor y sus registros relacionados fueron eliminados correctamente.")
            limpiar_campos()

        except Exception as e:
            # En caso de un error, revertir todos los cambios
            conn.rollback()
            messagebox.showerror("Error", f"Ocurrió un error al eliminar al profesor: {e}")

        finally:
            conn.close()

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

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        midName.delete(0, tk.END)
        lasName.delete(0, tk.END)
        emailEntry.delete(0, tk.END)
        carreraListbox.selection_clear(0, tk.END)
        materiaListbox.selection_clear(0, tk.END)
        studyGrade.set('')
        

        # Configuración de la ventana principal

    teacherWindow = tk.Tk()
    teacherWindow.title("Gestión de Maestros")
    teacherWindow.geometry("600x600")


    # Información del maestro
    tk.Label(teacherWindow, text="ID de Maestro:").grid(row=1, column=0)
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

    tk.Label(teacherWindow, text="Correo:").grid(row=5, column=0)
    emailEntry = tk.Entry(teacherWindow)
    emailEntry.grid(row=5, column=1)

    tk.Label(teacherWindow, text="Grado de Estudio:").grid(row=6, column=0)
    studyGrade = ttk.Combobox(teacherWindow, values=["Licenciatura", "Maestría", "Doctorado"])
    studyGrade.grid(row=6, column=1)

    tk.Label(teacherWindow, text="Carreras:").grid(row=7, column=0)
    carreraListbox = tk.Listbox(teacherWindow, selectmode=tk.SINGLE, exportselection=0)
    carreraListbox.grid(row=7, column=1)

    tk.Label(teacherWindow, text="Materias:").grid(row=8, column=0)
    materiaListbox = tk.Listbox(teacherWindow, selectmode=tk.MULTIPLE, exportselection=0)
    materiaListbox.grid(row=8, column=1)


    # Cargar las carreras en el Combobox al iniciar la ventana
    def cargar_carreras():
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT nombre_carrera FROM Carreras")
            carreras = [row[0] for row in cursor.fetchall()]

            # Limpiar el Listbox antes de cargar los nuevos elementos
            carreraListbox.delete(0, tk.END)

            # Insertar los valores en el Listbox
            for carrera in carreras:
                carreraListbox.insert(tk.END, carrera)

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
    if(rol!= "maestro"):
        cargar_carreras()
        cargar_materias()

    def validarRolMaestro(id_usuario):
        conn = conectar()
        cursor = conn.cursor()
        try:
            # Validar que el id_usuario es del tipo maestro en Usuarios
            cursor.execute("SELECT tipo_usuario FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
            resultado = cursor.fetchone()
            if not resultado or resultado[0] != 'maestro':  # Corregido 'alumno' a 'maestro'
                return False
        except Exception as e:
            messagebox.showinfo("Error", f"Error al validar: {str(e)}")
            return False
        finally:
            conn.close()

        return True

    def validarMaestro(id_usuario):
        conn = conectar()
        cursor = conn.cursor()

        try:
            # Validar que el id_usuario es del tipo maestro en Usuarios
            cursor.execute("SELECT tipo_usuario FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
            resultado = cursor.fetchone()
            if not resultado or resultado[0] != 'maestro':  # Corregido 'maeestro' a 'maestro'
                return False

            # Validar que el id_usuario ya tiene un registro en Maestros
            cursor.execute("SELECT * FROM Maestros WHERE id_usuario = ?", (id_usuario,))
            maestro = cursor.fetchone()
            if maestro:
                return False

        except Exception as e:
            messagebox.showinfo("Error", f"Error al validar: {str(e)}")
            return False
        finally:
            conn.close()

        return True

    def buscar_maestro(id_usuario):
        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT * FROM Maestros WHERE id_usuario = ?", (id_usuario,))
            maestro = cursor.fetchone()

            if maestro:
                # Validar si algunos valores son nulos
                idEntry.delete(0, tk.END)
                idEntry.insert(tk.END, maestro[0])

                nameEntry.delete(0, tk.END)
                nameEntry.insert(tk.END, maestro[1])

                midName.delete(0, tk.END)
                midName.insert(tk.END, maestro[2])

                lasName.delete(0, tk.END)
                lasName.insert(tk.END, maestro[3])

                emailEntry.delete(0, tk.END)
                emailEntry.insert(tk.END, maestro[4])

                carreraListbox.set(maestro[5])  # Combobox para carrera
                studyGrade.set(maestro[6])  # Grado de estudios
                messagebox.showinfo("Éxito", "Maestro encontrado")
            else:
                messagebox.showinfo("No Encontrado", "No se encontró un maestro con ese ID")

        except Exception as e:
            messagebox.showinfo("Error", f"Error al buscar el maestro: {str(e)}")
        finally:
            conn.close()

    def agregar_cuentaMaestro(id_usuario):
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

            # Validar que el correo no exista en Maestros
            cursor.execute("SELECT * FROM Maestros WHERE correo = ?", (correo,))
            if cursor.fetchone():
                messagebox.showinfo("Error", "El correo ya está registrado como maestro.")
                return

            # Generar un nuevo ID único para el maestro
            cursor.execute("SELECT id_maestro FROM Maestros ORDER BY id_maestro")
            ids_existentes = [row[0] for row in cursor.fetchall()]

            siguiente_id = 1
            for id_ in ids_existentes:
                if id_ == siguiente_id:
                    siguiente_id += 1

            # Insertar en la tabla Maestros
            cursor.execute(
                "INSERT INTO Maestros (id_maestro, nombre, a_paterno, a_materno, correo, id_usuario) VALUES (?, ?, ?, ?, ?, ?)",
                (siguiente_id, nombre, a_paterno, a_materno, correo, id_usuario)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Maestro registrado correctamente.")
        except Exception as e:
            messagebox.showinfo("Error", f"No se pudo registrar al maestro: {str(e)}")
        finally:
            conn.close()
    def limpiar_camposMAestro():
        limpiar_campos()
        cargar_carreras()
        cargar_materias()
        buscar_maestro(id_usuario)


    if(rol!="maestro"):
            # ID del maestro para búsquedas
        tk.Label(teacherWindow, text="ID de Maestro:").grid(row=0, column=0)
        idSearch = tk.Entry(teacherWindow)
        idSearch.grid(row=0, column=1)
        tk.Button(teacherWindow, text="Buscar", command=buscar_profesor).grid(row=0, column=2)

        tk.Button(teacherWindow, text="Agregar", command=agregar_maestro).grid(row=9, column=0, columnspan=2)
        tk.Button(teacherWindow, text="Editar Maestro", command=editar_maestro).grid(row=9, column=2)
        tk.Button(teacherWindow, text="Eliminar Maestro", command=eliminar_profesor).grid(row=9, column=3)
        tk.Button(teacherWindow, text="Limpiar Campos", command=limpiar_campos).grid(row=10, column=1)
        tk.Button(teacherWindow, text='Nuevo Maestro', command=obtener_siguiente_id).grid(row=10, column=2)
    else:
        limpiar_camposMAestro()
        idEntry.config(state="disabled")
        emailEntry.config(state="disabled")
        #carreraListbox.config(state="disabled")
        materiaListbox.config(state="disabled")

        tk.Button(teacherWindow, text="Guardar Cambios", command=editar_maestro).grid(row=9, column=1)
        tk.Button(teacherWindow, text="Cancelar", command=limpiar_camposMAestro).grid(row=10, column=1)
        conn = conectar()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT Creado FROM GrupoCreado WHERE grupo = 1")
            resultado = cursor.fetchone()

            if resultado and resultado[0] == 1:  
                materiaListbox.config(state="disabled")  
            else:
                materiaListbox.config(state="normal")  
        except Exception as e:
            print(f"Error al verificar la base de datos: {e}")
        finally:
            conn.close()
    teacherWindow.mainloop()