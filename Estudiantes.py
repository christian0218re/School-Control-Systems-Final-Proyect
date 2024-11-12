import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
from DataBase import conectar
import re

studentWindow = None

def createStudentWindow():
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
        materia = subEntry.get()

        # Verificar que todos los campos están completos
        if not (id_estudiante and nombre and a_paterno and a_materno and email and estado and fechaNac and carrera and materia):
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
                "INSERT INTO Alumnos (id_alumno, nombre, fecha_nacimiento, A_paterno, A_materno, carrera, estado, correo)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (id_estudiante, nombre, fechaNac, a_paterno, a_materno, carrera, estado, email)
            )
            conn.commit()
            messagebox.showinfo("Éxito", "Alumno registrado correctamente")
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

            # Verificar que el correo no esté ya registrado
        cursor.execute("SELECT * FROM Alumnos WHERE correo = ?", (email,))
        if cursor.fetchone():
            messagebox.showinfo("Error", "El correo electrónico ya está registrado")
            return

        try:
            cursor.execute("UPDATE Alumnos SET nombre = ?, fecha_nacimiento = ?, A_paterno = ?, A_materno = ?, carrera = ?, estado = ?, correo = ? WHERE id_alumno = ?",
                           (nombre, fechaNac, a_paterno, a_materno, carrera, estado, email, id_estudiante))
            conn.commit()
            messagebox.showinfo("Éxito", "Alumno actualizado correctamente")
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
        subEntry.set("")

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

    studentWindow = tk.Toplevel()
    studentWindow.title("Gestión de Estudiantes")
    studentWindow.geometry("600x500")

    tk.Label(studentWindow, text="Ingrese código de alumno").grid(row=1, column=0)
    idEntryBusqueda = tk.Entry(studentWindow)
    idEntryBusqueda.grid(row=1, column=1)
    tk.Button(studentWindow, text='Buscar', command=buscar_estudiante).grid(row=1, column=2)

    tk.Label(studentWindow, text='ID').grid(row=3, column=0)
    idEntry = tk.Entry(studentWindow)
    idEntry.grid(row=3, column=1)

    tk.Label(studentWindow, text='Nombre').grid(row=4, column=0)
    nameEntry = tk.Entry(studentWindow)
    nameEntry.grid(row=4, column=1)

    tk.Label(studentWindow, text='A. Paterno').grid(row=5, column=0)
    midNameEntry = tk.Entry(studentWindow)
    midNameEntry.grid(row=5, column=1)

    tk.Label(studentWindow, text='A. Materno').grid(row=6, column=0)
    lasNameEntry = tk.Entry(studentWindow)
    lasNameEntry.grid(row=6, column=1)

    tk.Label(studentWindow, text='Email').grid(row=7, column=0)
    emailEntry = tk.Entry(studentWindow)
    emailEntry.grid(row=7, column=1)

    tk.Label(studentWindow, text='Estado').grid(row=3, column=3)
    stateEntry = tk.Entry(studentWindow)
    stateEntry.grid(row=3, column=4)

    tk.Label(studentWindow, text='Fecha Nac').grid(row=4, column=3)
    birthEntry = DateEntry(studentWindow, date_pattern='yyyy-mm-dd')
    birthEntry.grid(row=4, column=4)

    tk.Label(studentWindow, text='Carrera').grid(row=5, column=3)
    career_data = obtener_datos("SELECT nombre_carrera FROM Carreras")
    careerEntry = ttk.Combobox(studentWindow, values=career_data)
    careerEntry.grid(row=5, column=4)

    tk.Label(studentWindow, text='Materia').grid(row=6, column=3)
    subject_data = obtener_datos("SELECT nombre_materia FROM Materias")
    subEntry = ttk.Combobox(studentWindow, values=subject_data)
    subEntry.grid(row=6, column=4)

    tk.Button(studentWindow, text="Nuevo", command=obtener_siguiente_id).grid(row=9, column=1)
    tk.Button(studentWindow, text="Guardar", command=agregar_estudiante).grid(row=9, column=2)
    tk.Button(studentWindow, text="Cancelar", command=limpiar_campos).grid(row=9, column=3)
    tk.Button(studentWindow, text="Editar", command=editar_estudiante).grid(row=9, column=4)
    tk.Button(studentWindow, text="Baja", command=eliminar_estudiante).grid(row=9, column=5)

    studentWindow.mainloop()