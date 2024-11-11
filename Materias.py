import tkinter as tk
from tkinter import messagebox, ttk
from DataBase import conectar


def createMateriaWindow():
    def agregar_materia():
        conn = conectar()
        cursor = conn.cursor()

        id_materia = idEntry.get()
        nombre_materia = nameEntry.get()
        codigo_materia = codeEntry.get()
        creditos = creditEntry.get()
        semestre = semesterEntry.get()

        if not (id_materia and nombre_materia and codigo_materia and creditos and semestre):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        try:
            cursor.execute("INSERT INTO Materias (id_materia, nombre_materia, codigo_materia, creditos, semestre)"
                           " VALUES (?, ?, ?, ?, ?)", (id_materia, nombre_materia, codigo_materia, creditos, semestre))
            conn.commit()
            messagebox.showinfo("Éxito", "Materia registrada correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def buscar_materia():
        conn = conectar()
        cursor = conn.cursor()
        materia_id = idEntryBusqueda.get()

        if not materia_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de materia")
            return

        cursor.execute("SELECT * FROM Materias WHERE id_materia = ?", (materia_id,))
        materia = cursor.fetchone()

        if materia:
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, materia[0])
            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, materia[1])
            codeEntry.delete(0, tk.END)
            codeEntry.insert(tk.END, materia[2])
            creditEntry.delete(0, tk.END)
            creditEntry.insert(tk.END, materia[3])
            semesterEntry.delete(0, tk.END)
            semesterEntry.insert(tk.END, materia[4])
            messagebox.showinfo("Éxito", "Materia encontrada y datos llenados")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró una materia con ese ID")

        conn.close()

    def editar_materia():
        conn = conectar()
        cursor = conn.cursor()

        id_materia = idEntry.get()
        nombre_materia = nameEntry.get()
        codigo_materia = codeEntry.get()
        creditos = creditEntry.get()
        semestre = semesterEntry.get()

        if not (id_materia and nombre_materia and codigo_materia and creditos and semestre):
            messagebox.showinfo("Error", "Por favor, rellene todos los campos")
            return

        try:
            cursor.execute(
                "UPDATE Materias SET nombre_materia = ?, codigo_materia = ?, creditos = ?, semestre = ? WHERE id_materia = ?",
                (nombre_materia, codigo_materia, creditos, semestre, id_materia))
            conn.commit()
            messagebox.showinfo("Éxito", "Materia actualizada correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_materia():
        conn = conectar()
        cursor = conn.cursor()
        id_materia = idEntry.get()

        if not id_materia:
            messagebox.showinfo("Error", "Por favor, busque una materia para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar esta materia?")
        if not confirmacion:
            return

        try:
            cursor.execute("DELETE FROM Materias WHERE id_materia = ?", (id_materia,))
            conn.commit()
            messagebox.showinfo("Éxito", "Materia eliminada correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        codeEntry.delete(0, tk.END)
        creditEntry.delete(0, tk.END)
        semesterEntry.delete(0, tk.END)

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_materia FROM Materias ORDER BY id_materia")
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

    materiaWindow = tk.Toplevel()
    materiaWindow.title("Gestión de Materias")
    materiaWindow.geometry("600x500")

    tk.Label(materiaWindow, text="Ingrese código de materia").grid(row=1, column=0)
    idEntryBusqueda = tk.Entry(materiaWindow)
    idEntryBusqueda.grid(row=1, column=1)
    tk.Button(materiaWindow, text='Buscar', command=buscar_materia).grid(row=1, column=2)

    tk.Label(materiaWindow, text='ID').grid(row=3, column=0)
    idEntry = tk.Entry(materiaWindow)
    idEntry.grid(row=3, column=1)

    tk.Label(materiaWindow, text='Nombre de Materia').grid(row=4, column=0)
    nameEntry = tk.Entry(materiaWindow)
    nameEntry.grid(row=4, column=1)

    tk.Label(materiaWindow, text='Código de Materia').grid(row=5, column=0)
    codeEntry = tk.Entry(materiaWindow)
    codeEntry.grid(row=5, column=1)

    tk.Label(materiaWindow, text='Créditos').grid(row=6, column=0)
    creditEntry = tk.Entry(materiaWindow)
    creditEntry.grid(row=6, column=1)

    tk.Label(materiaWindow, text='Semestre').grid(row=7, column=0)
    semesterEntry = tk.Entry(materiaWindow)
    semesterEntry.grid(row=7, column=1)

    tk.Button(materiaWindow, text="Nuevo", command=obtener_siguiente_id).grid(row=9, column=1)
    tk.Button(materiaWindow, text="Guardar", command=agregar_materia).grid(row=9, column=2)
    tk.Button(materiaWindow, text="Cancelar", command=limpiar_campos).grid(row=9, column=3)
    tk.Button(materiaWindow, text="Editar", command=editar_materia).grid(row=9, column=4)
    tk.Button(materiaWindow, text="Baja", command=eliminar_materia).grid(row=9, column=5)

    materiaWindow.mainloop()
