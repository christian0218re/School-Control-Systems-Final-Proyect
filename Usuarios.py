import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from DataBase import conectar
import re

def createUserWindow():
    def obtener_siguiente_idd(tabla):
        conn = conectar()
        cursor = conn.cursor()
        
        # Determinar la columna de ID según la tabla
        if tabla == "Alumnos":
            columna_id = "id_alumno"
        elif tabla == "Maestros":
            columna_id = "id_maestro"
        else:
            raise ValueError("Tabla no válida")
        
        # Ejecutar consulta para obtener IDs existentes
        cursor.execute(f"SELECT {columna_id} FROM {tabla} ORDER BY {columna_id}")
        ids_existentes = [row[0] for row in cursor.fetchall()]
        
        # Encontrar el siguiente ID disponible
        if not ids_existentes:
            siguiente_id = 1
        else:
            siguiente_id = max(ids_existentes) + 1
        
        conn.close()
        return siguiente_id
    def agregar_usuario():
        conn = conectar()
        cursor = conn.cursor()
        
        try:
            # Obtener valores de los campos de entrada
            id_usuario = idEntry.get()
            nombre = nameEntry.get()
            a_paterno = midNameEntry.get()
            a_materno = lasNameEntry.get()
            correo = emailEntry.get()
            nombre_usuario = usernameEntry.get()
            contrasena = passwordEntry.get()
            tipo_usuario = profileEntry.get().lower()  # Convertir a minúsculas
            
            # Validación de campos vacíos
            if not (id_usuario and nombre and a_paterno and a_materno and 
                    correo and nombre_usuario and contrasena and tipo_usuario):
                messagebox.showinfo("Error", "Por favor, rellene todos los campos")
                conn.close()
                return
            
            # Validación de formato de correo electrónico
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_regex, correo):
                messagebox.showinfo("Error", "El correo electrónico no tiene un formato válido")
                conn.close()
                return
            
            # Validación de nombre de usuario único
            cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE nombre_usuario = ?", (nombre_usuario,))
            if cursor.fetchone()[0] > 0:
                messagebox.showinfo("Error", "El nombre de usuario ya está en uso. Elija otro nombre de usuario.")
                conn.close()
                return
            
            # Insertar usuario en la tabla Usuarios
            cursor.execute(
                "INSERT INTO Usuarios (id_usuario, nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id_usuario, nombre, a_paterno, a_materno, correo, nombre_usuario, contrasena, tipo_usuario)
            )
            
            # Inserción adicional según el tipo de usuario
            if tipo_usuario == "maestro":
                # Crear una nueva ventana para información adicional de maestros
                maestro_window = tk.Toplevel()
                maestro_window.title("Información Adicional de Maestro")
                maestro_window.geometry("300x200")
                
                # Etiqueta y entrada para grado de estudio
                tk.Label(maestro_window, text="Grado de Estudio:").pack()
                grado_estudio_var = tk.StringVar()
                grado_estudio_combo = ttk.Combobox(maestro_window, 
                    textvariable=grado_estudio_var, 
                    values=["Licenciatura", "Maestria", "Doctorado"])
                grado_estudio_combo.pack()
                
                def guardar_maestro():
                    grado_estudio = grado_estudio_var.get()
                    
                    # Validar que el grado de estudio sea válido
                    if not grado_estudio:
                        messagebox.showinfo("Error", "Seleccione un grado de estudio")
                        return
                    
                    try:
                        idMaestro=obtener_siguiente_idd("Maestros")
                        # Insertar en la tabla Maestros
                        cursor.execute(
                            "INSERT INTO Maestros (id_maestro,nombre, a_paterno, a_materno, correo, grado_estudio, id_usuario) "
                            "VALUES (?,?, ?, ?, ?, ?, ?)",
                            (idMaestro,nombre, a_paterno, a_materno, correo, grado_estudio, id_usuario)
                        )
                        conn.commit()
                        
                        # Imprimir la información del usuario recién creado
                        print(f"ID de Usuario creado: {id_usuario}")
                        
                        # Buscar y imprimir los detalles del maestro
                        cursor.execute("SELECT * FROM Maestros WHERE id_usuario = ?", (id_usuario,))
                        maestro = cursor.fetchone()
                        print("Detalles del Maestro:")
                        print(f"ID de Usuario: {maestro[5]}")
                        print(f"Nombre: {maestro[0]} {maestro[1]} {maestro[2]}")
                        print(f"Correo: {maestro[3]}")
                        print(f"Grado de Estudio: {maestro[4]}")
                        print(idMaestro)
                        messagebox.showinfo("Éxito", "Maestro registrado correctamente")
                        maestro_window.destroy()
                        limpiar_campos()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showinfo("Error", str(e))
                    finally:
                        conn.close()
                
                tk.Button(maestro_window, text="Guardar", command=guardar_maestro).pack()
            
            elif tipo_usuario == "alumno":
                # Crear una nueva ventana para información adicional de alumnos
                alumno_window = tk.Toplevel()
                alumno_window.title("Información Adicional de Alumno")
                alumno_window.geometry("300x350")  # Aumenté un poco el tamaño

                # Etiquetas y entradas para información adicional
                tk.Label(alumno_window, text="Carrera:").pack()
                
                # Crear un Combobox en lugar de un Entry para seleccionar carrera
                carrera_var = tk.StringVar()
                carrera_combobox = ttk.Combobox(alumno_window, textvariable=carrera_var, state="readonly")
                
                try:
                    cursor.execute("SELECT nombre_carrera FROM Carreras")
                    carreras = [row[0] for row in cursor.fetchall()]
                    carrera_combobox['values'] = carreras
                except Exception as e:
                    messagebox.showinfo("Error al cargar carreras", str(e))
                
                carrera_combobox.pack()

                def guardar_alumno():
                    carrera = carrera_var.get()  # Obtener la carrera seleccionada del Combobox
                    
                    try:
                        # Insertar en la tabla Alumnos
                        cursor.execute(
                            "INSERT INTO Alumnos (nombre, a_paterno, a_materno, carrera, correo, id_usuario) "
                            "VALUES (?, ?, ?, ?, ?, ?)",
                            (nombre, a_paterno, a_materno, carrera, correo, id_usuario)
                        )
                        conn.commit()
                        messagebox.showinfo("Éxito", "Alumno registrado correctamente")
                        alumno_window.destroy()
                        limpiar_campos()
                    except Exception as e:
                        conn.rollback()
                        messagebox.showinfo("Error", str(e))
                    finally:
                        conn.close()

                tk.Button(alumno_window, text="Guardar", command=guardar_alumno).pack()
                
            
            else:  # administrador
                conn.commit()
                messagebox.showinfo("Éxito", "Usuario registrado correctamente")
                limpiar_campos()
                conn.close()
        
        except Exception as e:
            # Revertir cualquier cambio en caso de error
            conn.rollback()
            messagebox.showinfo("Error", str(e))
            conn.close()

    def buscar_usuario():
        conn = conectar()
        cursor = conn.cursor()
        usuario_id = idEntryBusqueda.get()

        if not usuario_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de usuario")
            return

        cursor.execute("SELECT * FROM Usuarios WHERE id_usuario = ?", (usuario_id,))
        usuario = cursor.fetchone()

        if usuario:
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, usuario[0])
            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, usuario[1])
            midNameEntry.delete(0, tk.END)
            midNameEntry.insert(tk.END, usuario[2])
            lasNameEntry.delete(0, tk.END)
            lasNameEntry.insert(tk.END, usuario[3])
            emailEntry.delete(0, tk.END)
            emailEntry.insert(tk.END, usuario[4])
            usernameEntry.delete(0, tk.END)
            usernameEntry.insert(tk.END, usuario[5])
            passwordEntry.delete(0, tk.END)
            passwordEntry.insert(tk.END, usuario[6])
            profileEntry.set(usuario[7])
            messagebox.showinfo("Éxito", "Usuario encontrado y datos llenados")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un usuario con ese ID")

        conn.close()

    def editar_usuario():
        conn = conectar()
        cursor = conn.cursor()

        id_usuario = idEntry.get()
        nombre = nameEntry.get()
        a_paterno = midNameEntry.get()
        a_materno = lasNameEntry.get()
        correo = emailEntry.get()
        nombre_usuario = usernameEntry.get()
        contrasena = passwordEntry.get()
        tipo_usuario = profileEntry.get()

        if not (
                id_usuario and nombre and a_paterno and a_materno and correo and nombre_usuario and contrasena and tipo_usuario):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

            # Validación de formato de correo electrónico
            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_regex, correo):
                messagebox.showinfo("Error", "El correo electrónico no tiene un formato válido")
                return

            # Validación de nombre de usuario único
            #cursor.execute("SELECT COUNT(*) FROM Usuarios WHERE nombre_usuario = ?", (nombre_usuario,))
            #if cursor.fetchone()[0] > 0:
            #    messagebox.showinfo("Error", "El nombre de usuario ya está en uso. Elija otro nombre de usuario.")
            #    return

            # Validación de la contraseña
            password_regex = r'^(?=.*[A-Z])(?=.*[!@#$%^&*()_+{}:"<>?]).{6,}$'
            if not re.match(password_regex, contrasena):
                messagebox.showinfo("Error",
                                    "La contraseña debe tener al menos 6 caracteres, una letra mayúscula y un carácter especial")
                return

        try:
            cursor.execute(
                "UPDATE Usuarios SET nombre = ?, a_paterno = ?, a_materno = ?, correo = ?, nombre_usuario = ?, contraseña = ?, tipo_usuario = ? WHERE id_usuario = ?",
                (nombre, a_paterno, a_materno, correo, nombre_usuario, contrasena, tipo_usuario, id_usuario))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario actualizado correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_usuario():
        conn = conectar()
        cursor = conn.cursor()
        id_usuario = idEntry.get()

        if not id_usuario:
            messagebox.showinfo("Error", "Por favor, busque un usuario para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este usuario?")
        if not confirmacion:
            return

        try:
            cursor.execute("DELETE FROM Usuarios WHERE id_usuario = ?", (id_usuario,))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
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
        usernameEntry.delete(0, tk.END)
        passwordEntry.delete(0, tk.END)
        profileEntry.set("")

    def obtener_datos(query):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(query)
        data = [row[0] for row in cursor.fetchall()]
        conn.close()
        return data

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_usuario FROM Usuarios ORDER BY id_usuario")
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

    userWindow = tk.Toplevel()
    userWindow.title("Gestión de Usuarios")
    userWindow.geometry("600x500")

    tk.Label(userWindow, text="Ingrese código de usuario").grid(row=1, column=0)
    idEntryBusqueda = tk.Entry(userWindow)
    idEntryBusqueda.grid(row=1, column=1)
    tk.Button(userWindow, text='Buscar', command=buscar_usuario).grid(row=1, column=2)

    tk.Label(userWindow, text='ID').grid(row=3, column=0)
    idEntry = tk.Entry(userWindow)
    idEntry.grid(row=3, column=1)

    tk.Label(userWindow, text='Nombre').grid(row=4, column=0)
    nameEntry = tk.Entry(userWindow)
    nameEntry.grid(row=4, column=1)

    tk.Label(userWindow, text='A. Paterno').grid(row=5, column=0)
    midNameEntry = tk.Entry(userWindow)
    midNameEntry.grid(row=5, column=1)

    tk.Label(userWindow, text='A. Materno').grid(row=6, column=0)
    lasNameEntry = tk.Entry(userWindow)
    lasNameEntry.grid(row=6, column=1)

    tk.Label(userWindow, text='Correo').grid(row=7, column=0)
    emailEntry = tk.Entry(userWindow)
    emailEntry.grid(row=7, column=1)

    tk.Label(userWindow, text='Nombre de usuario').grid(row=3, column=3)
    usernameEntry = tk.Entry(userWindow)
    usernameEntry.grid(row=3, column=4)

    tk.Label(userWindow, text='Contraseña').grid(row=4, column=3)
    passwordEntry = tk.Entry(userWindow, show="*")
    passwordEntry.grid(row=4, column=4)

    tk.Label(userWindow, text='Tipo de usuario').grid(row=5, column=3)
    profileEntry = ttk.Combobox(userWindow, values=["administrador", "maestro", "alumno"])
    profileEntry.grid(row=5, column=4)


    tk.Button(userWindow, text="Nuevo", command=obtener_siguiente_id).grid(row=9, column=1)
    tk.Button(userWindow, text="Guardar", command=agregar_usuario).grid(row=9, column=2)
    tk.Button(userWindow, text="Cancelar", command=limpiar_campos).grid(row=9, column=3)
    tk.Button(userWindow, text="Editar", command=editar_usuario).grid(row=9, column=4)
    tk.Button(userWindow, text="Baja", command=eliminar_usuario).grid(row=9, column=5)

    userWindow.mainloop()
