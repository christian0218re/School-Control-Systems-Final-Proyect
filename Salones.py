import tkinter as tk
from tkinter import messagebox, ttk
from DataBase import conectar

def createClassroomWindow():
    def agregar_salon():
        conn = conectar()
        cursor = conn.cursor()

        id_salon = idEntry.get()
        numero = numbEntry.get()
        capacidad = capEntry.get()
        edificio = buildEntry.get()

        # Validación de campos vacíos
        if not (id_salon and numero and capacidad and edificio):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación de número de salón único dentro del edificio
        cursor.execute("SELECT COUNT(*) FROM Salones WHERE numero_salon = ? AND ubicacion = ?", (numero, edificio))
        if cursor.fetchone()[0] > 0:
            messagebox.showinfo("Error", "El salón ya existe en este edificio. Elija otro número de salón o cambie el edificio.")
            return

        try:
            # Insertar usuario si las validaciones son correctas
            cursor.execute(
                "INSERT INTO Salones (id_salon, numero_salon, capacidad, ubicacion) VALUES (?, ?, ?, ?)",
                (id_salon, numero, capacidad, edificio)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Aula registrada correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def buscar_salon():
        conn = conectar()
        cursor = conn.cursor()
        busqueda = searchEntry.get()

        if not busqueda:
            messagebox.showinfo("Error", "Por favor ingrese un ID de salón")
            return

        cursor.execute("SELECT * FROM Salones WHERE id_salon = ?", (busqueda,))
        salon = cursor.fetchone()

        if salon:
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, salon[0])
            numbEntry.delete(0, tk.END)
            numbEntry.insert(tk.END, salon[1])
            capEntry.delete(0, tk.END)
            capEntry.insert(tk.END, salon[2])
            buildEntry.delete(0, tk.END)
            buildEntry.insert(tk.END, salon[3])
            messagebox.showinfo("Éxito", "Aula encontrada y datos llenados")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un aula con ese ID")

        conn.close()

    def editar_salon():
        conn = conectar()
        cursor = conn.cursor()

        id_salon = idEntry.get()
        numero = numbEntry.get()
        capacidad = capEntry.get()
        edificio = buildEntry.get()

        if not (id_salon and numero and capacidad and edificio):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        # Validación de número de salón único dentro del edificio
        cursor.execute("SELECT COUNT(*) FROM Salones WHERE numero_salon = ? AND ubicacion = ? AND id_salon != ?",
                       (numero, edificio, id_salon))
        if cursor.fetchone()[0] > 0:
            messagebox.showinfo("Error", "El salón ya existe en este edificio. Elija otro número de salón o cambie el edificio.")
            return

        try:
            cursor.execute(
                "UPDATE Salones SET numero_salon = ?, capacidad = ?, ubicacion = ? WHERE id_salon = ?",
                (numero, capacidad, edificio, id_salon)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Aula actualizada correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_salon():
        conn = conectar()
        cursor = conn.cursor()
        id_salon = idEntry.get()

        if not id_salon:
            messagebox.showinfo("Error", "Por favor, busque un aula para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este aula?")
        if not confirmacion:
            return

        try:
            cursor.execute("DELETE FROM Salones WHERE id_salon = ?", (id_salon,))
            conn.commit()
            messagebox.showinfo("Éxito", "Aula eliminada correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        searchEntry.delete(0, tk.END)
        numbEntry.delete(0, tk.END)
        capEntry.delete(0, tk.END)
        buildEntry.delete(0, tk.END)

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_salon FROM Salones ORDER BY id_salon")
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

    classroomWindow = tk.Toplevel()
    classroomWindow.title("Salones")
    classroomWindow.geometry("600x450")

    tk.Label(classroomWindow, text='Ingrese el ID del salon').grid(row=2, column=1)
    searchEntry = tk.Entry(classroomWindow)
    searchEntry.grid(row=2, column=2)
    tk.Button(classroomWindow, text='Buscar', command=buscar_salon).grid(row=2, column=3)

    tk.Label(classroomWindow, text='Ingrese el ID del salon').grid(row=3, column=1)
    idEntry = tk.Entry(classroomWindow)
    idEntry.grid(row=3, column=2)

    tk.Label(classroomWindow, text='Ingrese el numero del salon').grid(row=4, column=1)
    numbEntry = tk.Entry(classroomWindow)
    numbEntry.grid(row=4, column=2)

    tk.Label(classroomWindow, text='Ingrese la capacidad total del salon').grid(row=5, column=1)
    capEntry = tk.Entry(classroomWindow)
    capEntry.grid(row=5, column=2)

    tk.Label(classroomWindow, text='Ingrese el edificio donde se encuentra el salon').grid(row=6, column=1)
    buildEntry = tk.Entry(classroomWindow)
    buildEntry.grid(row=6, column=2)

    tk.Button(classroomWindow, text='Nuevo', command=obtener_siguiente_id).grid(row=7, column=0)
    tk.Button(classroomWindow, text='Guardar', command=agregar_salon).grid(row=7, column=1)
    tk.Button(classroomWindow, text='Cancelar', command=limpiar_campos).grid(row=7, column=2)
    tk.Button(classroomWindow, text='Editar', command=editar_salon).grid(row=7, column=3)
    tk.Button(classroomWindow, text='Baja', command=eliminar_salon).grid(row=7, column=4)

    classroomWindow.mainloop()