import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from DataBase import conectar  
from datetime import date
def createGrupoWindow():

    def buscar_grupo():
        conn = conectar()
        cursor = conn.cursor()
        grupo_id = searchEntry.get()  
        if not grupo_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de grupo")
            return

        try:
            cursor.execute("""
                SELECT fecha, id_carrera, id_maestro, id_materia, id_salon, id_horario, semestre, max_alumnos 
                FROM Grupos WHERE id_grupo = ?
            """, (grupo_id,))
            
            grupo = cursor.fetchone()

            if grupo:
                idEntry.delete(0, tk.END)
                idEntry.insert(tk.END, grupo_id)
                idEntry.config(state="disabled")

                fechaEntry.delete(0, tk.END)
                fechaEntry.insert(tk.END, grupo[0])

                # Obtener el ID de la carrera
                cursor.execute("SELECT nombre_carrera FROM Carreras WHERE id_carrera = ?", (grupo[1],))
                carrera = cursor.fetchone()
                if carrera:
                    carrera_combobox.set(f"{carrera[0]} (ID: {grupo[1]})")

                # Obtener el ID del maestro
                cursor.execute("SELECT nombre FROM Maestros WHERE id_maestro = ?", (grupo[2],))
                maestro = cursor.fetchone()
                if maestro:
                    maestro_combobox.set(f"{maestro[0]} (ID: {grupo[2]})")

                # Obtener el ID de la materia
                cursor.execute("SELECT nombre_materia FROM Materias WHERE id_materia = ?", (grupo[3],))
                materia = cursor.fetchone()
                if materia:
                    materia_combobox.set(f"{materia[0]} (ID: {grupo[3]})")

                # Obtener el ID del salón
                cursor.execute("SELECT numero_salon FROM Salones WHERE id_salon = ?", (grupo[4],))
                salon = cursor.fetchone()
                if salon:
                    salon_combobox.set(f"{salon[0]} (ID: {grupo[4]})")

                cursor.execute("SELECT turno, hora_inicio, hora_fin, id_horario FROM Horarios WHERE id_horario = ?", (grupo[5],))
                horario = cursor.fetchone()
                if horario:
                    horario_combobox.set(f"{horario[0]} ({horario[1]} - {horario[2]}) (ID: {horario[3]})")


                semestreEntry.delete(0, tk.END)
                semestreEntry.insert(tk.END, grupo[6])

                maxAlumnosEntry.delete(0, tk.END)
                maxAlumnosEntry.insert(tk.END, grupo[7])

                messagebox.showinfo("Grupo Encontrado", f"Grupo '{grupo_id}' encontrado y campos llenados.")
            else:
                messagebox.showinfo("No Encontrado", "No se encontró un grupo con ese ID")

        except Exception as e:
            messagebox.showinfo("Error", f"Hubo un error al buscar el grupo: {e}")

        finally:
            conn.close()

    def validarHorarios(id_salon, id_horario_nuevo):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT hora_inicio, hora_fin FROM Horarios WHERE id_horario = ?", (id_horario_nuevo,))
        nuevo_horario = cursor.fetchone()
        if not nuevo_horario:
            return False, "El horario seleccionado no existe."

        hora_inicio_nuevo, hora_fin_nuevo = nuevo_horario

        cursor.execute("""
            SELECT h.hora_inicio, h.hora_fin, g.id_grupo
            FROM Grupos g
            JOIN Horarios h ON g.id_horario = h.id_horario
            WHERE g.id_salon = ?""", (id_salon,))
        horarios_ocupados = cursor.fetchall()

        for horario in horarios_ocupados:
            hora_inicio_existente, hora_fin_existente, id_grupo_existente = horario
            if (hora_inicio_nuevo < hora_fin_existente and hora_fin_nuevo > hora_inicio_existente):
                return False, f"El horario seleccionado se cruza con el grupo {id_grupo_existente} que tiene el horario de {hora_inicio_existente} a {hora_fin_existente} en este salón."

        return True, ""  



    def agregar_grupo():
        conn = conectar()
        cursor = conn.cursor()


        id_grupo = idEntry.get()
        fecha = fechaEntry.get()
        id_carrera = obtener_id_combobox(carrera_combobox)
        id_maestro = obtener_id_combobox(maestro_combobox)
        id_materia = obtener_id_combobox(materia_combobox)
        id_salon = obtener_id_combobox(salon_combobox)
        id_horario = obtener_id_combobox(horario_combobox)
        semestre = semestreEntry.get()
        max_alumnos = maxAlumnosEntry.get()

        if not fecha or not id_carrera or not id_maestro or not id_materia or not id_salon or not id_horario or not semestre or not max_alumnos:
            messagebox.showinfo("Error", "Por favor rellene todos los campos")
            return

        valido, mensaje = validarHorarios(id_salon, id_horario)

        if not valido:
            messagebox.showinfo("Error", mensaje) 
            return  

        try:
            max_alumnos = int(max_alumnos)
            if max_alumnos < 10:
                messagebox.showinfo("Error", "El número máximo de alumnos debe ser al menos 10")
                return
        except ValueError:
            messagebox.showinfo("Error", "El campo 'Máximo de Alumnos' debe ser un número válido")
            return

        try:
            semestre = int(semestre)
            if semestre < 1 or semestre > 10:  
                messagebox.showinfo("Error", "El semestre debe estar entre 1 y 10")
                return
        except ValueError:
            messagebox.showinfo("Error", "El campo 'Semestre' debe ser un número válido")
            return

        try:
            cursor.execute("""
                INSERT INTO Grupos (id_grupo, fecha, id_carrera, id_maestro, id_materia, id_salon, id_horario, semestre, max_alumnos)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_grupo, fecha, id_carrera, id_maestro, id_materia, id_salon, id_horario, semestre, max_alumnos))

            conn.commit()
            messagebox.showinfo("Éxito", "Grupo agregado correctamente")
            limpiar_campos()  
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def validarHorariosEditar(id_salon, id_horario_nuevo, grupo_id_editado=None):
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT hora_inicio, hora_fin FROM Horarios WHERE id_horario = ?", (id_horario_nuevo,))
        nuevo_horario = cursor.fetchone()
        if not nuevo_horario:
            return False, "El horario seleccionado no existe."

        hora_inicio_nuevo, hora_fin_nuevo = nuevo_horario

        cursor.execute("""
            SELECT h.hora_inicio, h.hora_fin, g.id_grupo
            FROM Grupos g
            JOIN Horarios h ON g.id_horario = h.id_horario
            WHERE g.id_salon = ? AND g.id_grupo != ?""", (id_salon, grupo_id_editado))
        
        horarios_ocupados = cursor.fetchall()

        for horario in horarios_ocupados:
            hora_inicio_existente, hora_fin_existente, id_grupo_existente = horario
            if (hora_inicio_nuevo < hora_fin_existente and hora_fin_nuevo > hora_inicio_existente):
                return False, f"El horario seleccionado se cruza con el grupo {id_grupo_existente} que tiene el horario de {hora_inicio_existente} a {hora_fin_existente} en este salón."

        return True, ""


    def editar_grupo():
        conn = conectar()
        cursor = conn.cursor()

        grupo_id = idEntry.get()  
        fecha = fechaEntry.get()
        id_carrera = obtener_id_combobox(carrera_combobox)
        id_maestro = obtener_id_combobox(maestro_combobox)
        id_materia = obtener_id_combobox(materia_combobox)
        id_salon = obtener_id_combobox(salon_combobox)
        id_horario = obtener_id_combobox(horario_combobox)
        semestre = semestreEntry.get()
        max_alumnos = maxAlumnosEntry.get()

       
        if not fecha or not id_carrera or not id_maestro or not id_materia or not id_salon or not id_horario or not semestre or not max_alumnos:
            messagebox.showinfo("Error", "Por favor rellene todos los campos")
            return
       
        valido, mensaje = validarHorariosEditar(id_salon, id_horario, grupo_id)

        if not valido:
            messagebox.showinfo("Error", mensaje)  
            return  

        try:
            max_alumnos = int(max_alumnos)
            if max_alumnos < 10:
                messagebox.showinfo("Error", "El número máximo de alumnos debe ser al menos 10")
                return
        except ValueError:
            messagebox.showinfo("Error", "El campo 'Máximo de Alumnos' debe ser un número válido")
            return
        try:
            semestre = int(semestre)
            if semestre < 1 or semestre > 10:  # Validar que esté entre 1 y 10
                messagebox.showinfo("Error", "El semestre debe estar entre 1 y 10")
                return
        except ValueError:
            messagebox.showinfo("Error", "El campo 'Semestre' debe ser un número válido")
            return

        try:
            cursor.execute("""
                UPDATE Grupos
                SET fecha = ?, id_carrera = ?, id_maestro = ?, id_materia = ?, id_salon = ?, id_horario = ?, semestre = ?, max_alumnos = ?
                WHERE id_grupo = ?
            """, (fecha, id_carrera, id_maestro, id_materia, id_salon, id_horario, semestre, max_alumnos, grupo_id))

            conn.commit()

            if cursor.rowcount > 0:  
                messagebox.showinfo("Éxito", f"Grupo '{grupo_id}' editado correctamente")
            else:
                messagebox.showinfo("Error", f"No se encontró el grupo con ID '{grupo_id}' para editar")
            
            limpiar_campos()  
        except Exception as e:
            messagebox.showinfo("Error", f"Hubo un error al editar el grupo: {e}")
        finally:
            cancelar()
            conn.close()



    def eliminar_grupo():
        conn = conectar()
        cursor = conn.cursor()

        grupo_id = idEntry.get()  

        if not grupo_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de grupo")
            return

        try:
            cursor.execute("SELECT * FROM Grupos WHERE id_grupo = ?", (grupo_id,))
            grupo = cursor.fetchone()

            if grupo:
                
                cursor.execute("DELETE FROM Grupos WHERE id_grupo = ?", (grupo_id,))
                conn.commit()

                if cursor.rowcount > 0:  
                    messagebox.showinfo("Éxito", f"Grupo '{grupo_id}' eliminado correctamente")
                else:
                    messagebox.showinfo("Error", f"No se pudo eliminar el grupo con ID '{grupo_id}'")
            else:
                messagebox.showinfo("No Encontrado", f"No se encontró un grupo con ID '{grupo_id}' para eliminar")

            limpiar_campos()  #
        except Exception as e:
            messagebox.showinfo("Error", f"Hubo un error al eliminar el grupo: {e}")
        finally:
            conn.close()


    def limpiar_campos():
        pass

    def nuevo():
        try:
            
            conexion = conectar()
            cursor = conexion.cursor()

            
            cursor.execute("SELECT MAX(id_grupo) FROM Grupos")
            max_id = cursor.fetchone()[0]
            
            # Si no existe ningún grupo, empieza desde 1
            nuevo_id = max_id + 1 if max_id else 1
            
            cancelar()
            idEntry.insert(0, nuevo_id)
            conexion.close()
        
        except Exception as e:
            print(f"Error al generar un nuevo ID: {e}")

    def cancelar():
        # Limpiar todos los campos de texto 
        idEntry.config(state="normal")
        idEntry.delete(0, tk.END)
        fechaEntry.delete(0, tk.END)
        semestreEntry.delete(0, tk.END)
        maxAlumnosEntry.delete(0, tk.END)
        
        # Limpiar los combobox y poner su valor predeterminado
        carrera_combobox.set("Seleccione una carrera")
        maestro_combobox.set("Seleccione un maestro")
        materia_combobox.set("Seleccione una materia")
        salon_combobox.set("Seleccione un salón")
        horario_combobox.set("Seleccione un horario")


    def cargar_carreras_combobox(combobox):
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            cursor.execute("SELECT id_carrera, nombre_carrera FROM Carreras")
            carreras = cursor.fetchall()
            
            # Limpiar el combobox antes de agregar nuevos datos
            combobox['values'] = []
            for carrera in carreras:
                combobox['values'] = (*combobox['values'], f"{carrera[1]} (ID: {carrera[0]})")
            
            # Seleccionar un valor inicial vacío
            if carreras:
                combobox.set("Seleccione una carrera")
            conexion.close()
        except Exception as e:
            print(f"Error al cargar las carreras: {e}")

    def cargar_maestros_combobox(combobox, id_carrera):
        """
        Carga los maestros que están asignados a materias de la carrera seleccionada.
        """
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            query = """
                SELECT DISTINCT Maestros.id_maestro, 
                                Maestros.nombre || ' ' || Maestros.a_paterno || ' ' || Maestros.a_materno AS nombre_completo
                FROM Maestro_Carreras
                INNER JOIN Maestros ON Maestro_Carreras.id_maestro = Maestros.id_maestro
                INNER JOIN Maestro_Materias ON Maestros.id_maestro = Maestro_Materias.id_maestro
                INNER JOIN Materias_Carreras ON Maestro_Materias.id_materia = Materias_Carreras.id_materia
                WHERE Maestro_Carreras.id_carrera = ? AND Materias_Carreras.id_carrera = ?
            """
            # Ejecuta la consulta con el ID de carrera para verificar la relación
            cursor.execute(query, (id_carrera, id_carrera))
            maestros = cursor.fetchall()

            combobox['values'] = []
            for maestro in maestros:
                combobox['values'] = (*combobox['values'], f"{maestro[1]} (ID: {maestro[0]})")
            
            if maestros:
                combobox.set("Seleccione un maestro")
            else:
                combobox.set("No hay maestros disponibles")
            
            conexion.close()
        except Exception as e:
            print(f"Error al cargar los maestros: {e}")

    def actualizar_maestros(event):
        seleccion = carrera_combobox.get()
        if "ID:" in seleccion:
            # Extrae el ID de la carrera de la selección
            id_carrera = int(seleccion.split("ID:")[1].split(")")[0])
            cargar_maestros_combobox(maestro_combobox, id_carrera)
        else:
            maestro_combobox['values'] = []
            maestro_combobox.set("Seleccione una carrera primero")

    def cargar_materias_combobox(combobox, id_carrera, id_maestro):
        """
        Carga las materias que están asignadas al maestro y pertenecen a la carrera seleccionada.
        """
        try:
            conexion = conectar()
            cursor = conexion.cursor()
            
            query = """
                SELECT DISTINCT Materias.id_materia, Materias.nombre_materia
                FROM Materias_Carreras
                INNER JOIN Materias ON Materias_Carreras.id_materia = Materias.id_materia
                INNER JOIN Maestro_Materias ON Materias.id_materia = Maestro_Materias.id_materia
                WHERE Materias_Carreras.id_carrera = ? AND Maestro_Materias.id_maestro = ?
            """
            # Ejecuta la consulta con el ID de carrera y maestro para validar las relaciones
            cursor.execute(query, (id_carrera, id_maestro))
            materias = cursor.fetchall()

            combobox['values'] = []
            for materia in materias:
                combobox['values'] = (*combobox['values'], f"{materia[1]} (ID: {materia[0]})")
            
            if materias:
                combobox.set("Seleccione una materia")
            else:
                combobox.set("No hay materias disponibles")
            
            conexion.close()
        except Exception as e:
            print(f"Error al cargar las materias: {e}")

    def obtener_id_combobox(combobox):
        try:
            seleccion = combobox.get()  # Obtiene el texto seleccionado en el combobox
            if "(" in seleccion and "ID:" in seleccion:
                # Extrae el número después de 'ID: ' y antes del paréntesis de cierre
                id_value = seleccion.split("ID: ")[-1].strip(")")
                return int(id_value)  # Debería devolver el ID como entero
            else:
                return None  # Si el formato no es correcto, devuelve None
        except Exception as e:
            print(f"Error al obtener el ID del combobox: {e}")
            return None

    def actualizar_materias(event):
        id_carrera = obtener_id_combobox(carrera_combobox)
        id_maestro = obtener_id_combobox(maestro_combobox)
        
        if id_carrera and id_maestro:
            cargar_materias_combobox(materia_combobox, id_carrera, id_maestro)
        else:
            materia_combobox['values'] = []
            materia_combobox.set("Seleccione primero carrera y maestro")

    def cargar_salones_combobox(combobox):
        try:
            conexion = conectar()  
            cursor = conexion.cursor()

            cursor.execute("SELECT id_salon, numero_salon FROM Salones")
            salones = cursor.fetchall()
            
            salon_list = [f"{numero_salon} (ID: {id_salon})" for id_salon, numero_salon in salones]
            combobox['values'] = salon_list
            if salon_list:
                combobox.set(salon_list[0]) 
            
            conexion.close()
        except Exception as e:
            print(f"Error al cargar los salones: {e}")

    def cargar_horarios_combobox(combobox):
        try:
            conexion = conectar() 
            cursor = conexion.cursor()
            
            cursor.execute("SELECT id_horario, turno, hora_inicio, hora_fin FROM Horarios")
            horarios = cursor.fetchall()
            
            horario_list = [f"{turno} ({hora_inicio} - {hora_fin}) (ID: {id_horario})" for id_horario, turno, hora_inicio, hora_fin in horarios]
            combobox['values'] = horario_list
            if horario_list:
                combobox.set(horario_list[0]) 
            
            conexion.close()
        except Exception as e:
            print(f"Error al cargar los horarios: {e}")


    # Crear ventana de administración de grupos
    grupoWindow = tk.Toplevel()
    grupoWindow.title("Administración de Grupos")
    grupoWindow.geometry("800x600")

    # Frame para búsqueda de grupo
    search_frame = ttk.LabelFrame(grupoWindow, text="Buscar Grupo", padding="10")
    search_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    searchEntry = tk.Entry(search_frame, font=("Arial", 10))
    searchEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(search_frame, text="Buscar", font=("Arial", 10), command=buscar_grupo).grid(row=0, column=2, padx=5, pady=5)

    # Frame para detalles del grupo
    details_frame = ttk.LabelFrame(grupoWindow, text="Detalles del Grupo", padding="10")
    details_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    # Campos del formulario
    tk.Label(details_frame, text="ID del Grupo:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    idEntry = tk.Entry(details_frame, font=("Arial", 10))
    idEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Fecha:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    fechaEntry = DateEntry(details_frame, font=("Arial", 10), date_pattern='yyyy-mm-dd')
    fechaEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
    fechaEntry.set_date(date.today())
    # Combobox para Carrera, Maestro, Materia
    tk.Label(details_frame, text="Carrera:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    carrera_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    carrera_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    cargar_carreras_combobox(carrera_combobox)

    tk.Label(details_frame, text="Maestro:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    maestro_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    maestro_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")
    carrera_combobox.bind("<<ComboboxSelected>>", actualizar_maestros)

    tk.Label(details_frame, text="Materia:", font=("Arial", 10)).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    materia_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    materia_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
    maestro_combobox.bind("<<ComboboxSelected>>", actualizar_materias)

    # Label y combobox para Salón
    tk.Label(details_frame, text="Salón:", font=("Arial", 10)).grid(row=5, column=0, sticky="e", padx=5, pady=5)
    salon_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    salon_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="ew")
    cargar_salones_combobox(salon_combobox)

    # Label y combobox para Horario
    tk.Label(details_frame, text="Horario:", font=("Arial", 10)).grid(row=6, column=0, sticky="e", padx=5, pady=5)
    horario_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    horario_combobox.grid(row=6, column=1, padx=5, pady=5, sticky="ew")
    cargar_horarios_combobox(horario_combobox)

    # Otros campos: Semestre y Máximo de Alumnos
    tk.Label(details_frame, text="Semestre:", font=("Arial", 10)).grid(row=7, column=0, sticky="e", padx=5, pady=5)
    semestreEntry = tk.Entry(details_frame, font=("Arial", 10))
    semestreEntry.grid(row=7, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Máximo de Alumnos:", font=("Arial", 10)).grid(row=8, column=0, sticky="e", padx=5, pady=5)
    maxAlumnosEntry = tk.Entry(details_frame, font=("Arial", 10))
    maxAlumnosEntry.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

    # Frame para botones de acciones
    button_frame = tk.Frame(grupoWindow)
    button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

    # Subframe para centrar los botones
    button_subframe = tk.Frame(button_frame)
    button_subframe.pack(anchor="center")

    # Botones de acciones
    tk.Button(button_subframe, text="Nuevo", font=("Arial", 12), command=nuevo).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Agregar", font=("Arial", 12), command=agregar_grupo).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Cancelar", font=("Arial", 12), command=cancelar).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Editar", font=("Arial", 12), command=editar_grupo).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Baja", font=("Arial", 12), command=eliminar_grupo).pack(side="left", padx=5)
    cancelar()


'''
# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("250x100")  # Ajuste para que la ventana principal sea más compacta

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", font=("Arial", 10), command=createGrupoWindow).pack(padx=20, pady=20)

root.mainloop()'''