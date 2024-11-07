import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import MULTIPLE
from DataBase import conectar  # Asegúrate de que esta función de conexión está correcta

materias = None  # Definir la variable global de materias

def createCareerWindow():
    # Función para agregar una carrera
    def agregar_carrera():
        conn = conectar()
        cursor = conn.cursor()

        id_carrera = idEntry.get()
        nombre = nameEntry.get()

        if not nombre:
            messagebox.showinfo("Error", "Por favor rellene el campo de nombre de carrera")
            return

        try:
            cursor.execute("INSERT INTO Carreras (id_carrera, nombre_carrera) VALUES (?, ?)", (id_carrera, nombre))
            conn.commit()
            messagebox.showinfo("Éxito", "Carrera agregada correctamente")
            limpiar_campos()
            listar_carreras()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def listar_carreras():
        for row in tabla.get_children():
            tabla.delete(row)

        conn = conectar()
        cursor = conn.cursor()

        # Obtener todas las carreras
        cursor.execute("SELECT * FROM Carreras")
        carreras = cursor.fetchall()

        for carrera in carreras:
            carrera_id = carrera[0]
            
            # Obtener las materias asociadas a esta carrera
            cursor.execute("""
                SELECT m.nombre_materia
                FROM Materias_Carreras mc
                JOIN Materias m ON mc.id_materia = m.id_materia
                WHERE mc.id_carrera = ?
            """, (carrera_id,))
            materias = cursor.fetchall()

            # Depuración: Verifica si hay materias asociadas a la carrera
            print(f"Carrera ID: {carrera_id}, Nombre: {carrera[1]}, Materias: {materias}")

            if materias:
                # Crear una lista de las materias asociadas, separadas por comas
                materias_asociadas = ", ".join([materia[0] for materia in materias])
            else:
                materias_asociadas = "No hay materias asignadas"

            # Insertar la carrera en la tabla junto con las materias asociadas
            tabla.insert('', tk.END, values=(carrera_id, carrera[1], materias_asociadas), tags=("wrap",))

        conn.close()




    # Función para limpiar los campos de entrada
    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)

    # Función para obtener la carrera seleccionada desde el Treeview
    def obtener_carrera_seleccionada():
        selected_item = tabla.selection()  # Obtener la fila seleccionada en el Treeview
        if not selected_item:
            messagebox.showinfo("Error", "Por favor seleccione una carrera")
            return None
        carrera_id = tabla.item(selected_item, 'values')[0]  # Suponiendo que el ID de la carrera está en la primera columna
        return carrera_id

    # Función para asignar múltiples materias a una carrera
    def asignar_materias():
        carrera_id = obtener_carrera_seleccionada()  # Obtener el ID de la carrera seleccionada
        if carrera_id is None:
            return  # Si no hay una carrera seleccionada, no se realiza la asignación

        # Obtener las materias seleccionadas en el Listbox
        materias_seleccionadas = listboxMaterias.curselection()
        if not materias_seleccionadas:  # Verificar si no hay materias seleccionadas
            messagebox.showinfo("Error", "Por favor seleccione al menos una materia")
            return

        conn = conectar()
        cursor = conn.cursor()

        try:
            # Asignar cada materia seleccionada a la carrera
            for materia_index in materias_seleccionadas:
                materia_id = materias[materia_index][0]  # Obtiene el id_materia de la lista global 'materias'

                # Verificar si la materia ya está asignada a esta carrera
                cursor.execute("SELECT 1 FROM Materias_Carreras WHERE id_carrera = ? AND id_materia = ?", (carrera_id, materia_id))
                if cursor.fetchone():
                    messagebox.showinfo("Error", f"La materia '{materias[materia_index][1]}' ya está asignada a esta carrera")
                    continue  # Si ya está asignada, salta a la siguiente materia

                # Si la materia no está asignada, la asignamos a la carrera
                cursor.execute("INSERT INTO Materias_Carreras (id_carrera, id_materia) VALUES (?, ?)", (carrera_id, materia_id))
            
            # Confirmación de éxito
            conn.commit()
            messagebox.showinfo("Éxito", "Materias asignadas correctamente a la carrera")

            # Opcionalmente, puedes actualizar la vista o limpiar los campos después de asignar
            limpiar_campos()
            listar_carreras()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()


    # Función para eliminar materias de una carrera
    def eliminar_materias():
        carrera_id = idEntry.get()
        materias_seleccionadas = listboxMaterias.curselection()

        if not carrera_id or not materias_seleccionadas:
            messagebox.showinfo("Error", "Por favor seleccione una carrera y al menos una materia")
            return

        conn = conectar()
        cursor = conn.cursor()

        try:
            for materia_index in materias_seleccionadas:
                materia_id = materias[materia_index][0]  # Obtiene el id_materia
                cursor.execute("DELETE FROM Materias_Carreras WHERE id_carrera = ? AND id_materia = ?",
                               (carrera_id, materia_id))
            conn.commit()
            messagebox.showinfo("Éxito", "Materias eliminadas de la carrera correctamente")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Crear la ventana de administración de carreras y materias
    careerWindow = tk.Toplevel()
    careerWindow.title("Administración de Carreras")
    careerWindow.geometry("600x600")

    # Etiquetas y campos de entrada
    tk.Label(careerWindow, text="ID de la Carrera").grid(row=0, column=0, padx=10, pady=5)
    idEntry = tk.Entry(careerWindow)
    idEntry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(careerWindow, text="Nombre de la Carrera").grid(row=1, column=0, padx=10, pady=5)
    nameEntry = tk.Entry(careerWindow)
    nameEntry.grid(row=1, column=1, padx=10, pady=5)

    # Botón de agregar carrera
    tk.Button(careerWindow, text="Agregar Carrera", command=agregar_carrera).grid(row=2, column=0, padx=10, pady=5)

    # Tabla para mostrar carreras
    tabla = ttk.Treeview(careerWindow, columns=("ID", "Nombre de Carrera", "Materias"), show="headings", height=10)
    tabla.heading("ID", text="ID")
    tabla.heading("Nombre de Carrera", text="Nombre de Carrera")
    tabla.heading("Materias", text="Materias")

    # Ajustamos la columna de ID para que se ajuste al contenido
    tabla.column("ID", width=50, anchor="center")
    tabla.column("Nombre de Carrera", width=200, anchor="w")
    tabla.column("Materias", width=200, anchor="w")

    tabla.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
    # Listar las carreras existentes al abrir la ventana
    listar_carreras()

    # Materias y Carreras
    tk.Label(careerWindow, text="Asignar Materias a la Carrera").grid(row=4, column=0, padx=10, pady=5)

    # Listbox para seleccionar múltiples materias
    tk.Label(careerWindow, text="Seleccionar Materias").grid(row=5, column=0, padx=10, pady=5)
    listboxMaterias = tk.Listbox(careerWindow, selectmode=MULTIPLE, height=10)
    listboxMaterias.grid(row=5, column=1, padx=10, pady=5)

    # Cargar las materias en el listbox
    def cargar_materias():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_materia, nombre_materia FROM Materias")
        global materias
        materias = cursor.fetchall()  # Guardamos todas las materias en la variable global

        conn.close()

        # Limpiamos el Listbox antes de insertar las materias
        listboxMaterias.delete(0, tk.END)

        # Agregar las materias al Listbox
        for materia in materias:
            listboxMaterias.insert(tk.END, materia[1])  # Inserta solo el nombre de la materia


    cargar_materias()  # Llamamos a la función para cargar las materias al abrir la ventana

    # Botones para asignar y eliminar materias
    tk.Button(careerWindow, text="Asignar Materias", command=asignar_materias).grid(row=6, column=0, padx=10, pady=5)
    tk.Button(careerWindow, text="Eliminar Materias", command=eliminar_materias).grid(row=6, column=1, padx=10, pady=5)

    careerWindow.mainloop()

# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("200x100")

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", command=createCareerWindow).pack(padx=20, pady=20)

root.mainloop()
