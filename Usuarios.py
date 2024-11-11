import tkinter as tk
from tkinter import messagebox, ttk
from DataBase import conectar


def createUserWindow():
    def agregar_usuario():
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

        try:
            cursor.execute(
                "INSERT INTO Usuarios (id_usuario, nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id_usuario, nombre, a_paterno, a_materno, correo, nombre_usuario, contrasena, tipo_usuario))
            conn.commit()
            messagebox.showinfo("Éxito", "Usuario registrado correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
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
    profileEntry = ttk.Combobox(userWindow, values=["administrador", "maestro", "estudiante"])
    profileEntry.grid(row=5, column=4)


    tk.Button(userWindow, text="Nuevo", command=obtener_siguiente_id).grid(row=9, column=1)
    tk.Button(userWindow, text="Guardar", command=agregar_usuario).grid(row=9, column=2)
    tk.Button(userWindow, text="Cancelar", command=limpiar_campos).grid(row=9, column=3)
    tk.Button(userWindow, text="Editar", command=editar_usuario).grid(row=9, column=4)
    tk.Button(userWindow, text="Baja", command=eliminar_usuario).grid(row=9, column=5)

    userWindow.mainloop()
