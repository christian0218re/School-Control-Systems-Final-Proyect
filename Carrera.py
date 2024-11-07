import tkinter as tk
from tkinter import messagebox
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

        # Validar que el nombre no esté vacío
        if not nombre:
            messagebox.showinfo("Error", "Por favor rellene el campo de nombre de carrera")
            return

        # Verificar que se hayan seleccionado al menos una materia
        materias_seleccionadas = listboxMaterias.curselection()
        if not materias_seleccionadas:
            messagebox.showinfo("Error", "Por favor seleccione al menos una materia")
            return

        try:
            # Insertar la nueva carrera
            cursor.execute("INSERT INTO Carreras (id_carrera, nombre_carrera) VALUES (?, ?)", (id_carrera, nombre))
            conn.commit()

            # Asignar las materias seleccionadas a la nueva carrera
            for materia_index in materias_seleccionadas:
                materia_id = materias[materia_index][0]  # Obtener el id_materia de la lista global 'materias'
                cursor.execute("INSERT INTO Materias_Carreras (id_carrera, id_materia) VALUES (?, ?)", (id_carrera, materia_id))

            conn.commit()
            messagebox.showinfo("Éxito", "Carrera y materias agregadas correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Función para limpiar los campos de entrada
    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        listboxMaterias.selection_clear(0, tk.END)

    # Función para buscar carrera por ID y llenar los campos
    def buscar_carrera():
        conn = conectar()
        cursor = conn.cursor()
        carrera_id = searchEntry.get()  # Obtener el ID ingresado

        if not carrera_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de carrera")
            return

        # Consultar la carrera por el ID
        cursor.execute("SELECT nombre_carrera FROM Carreras WHERE id_carrera = ?", (carrera_id,))
        carrera = cursor.fetchone()

        if carrera:
            # Completar el campo de nombre de la carrera
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, carrera_id)
            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, carrera[0])

            # Buscar las materias asociadas a la carrera
            cursor.execute("""
                SELECT m.id_materia, m.nombre_materia 
                FROM Materias m
                JOIN Materias_Carreras mc ON m.id_materia = mc.id_materia
                WHERE mc.id_carrera = ?
            """, (carrera_id,))
            materias_asociadas = cursor.fetchall()

            # Limpiar la selección de materias en el listbox
            listboxMaterias.selection_clear(0, tk.END)

            # Seleccionar las materias asociadas a la carrera
            for materia in materias_asociadas:
                # Encontrar el índice de la materia en la lista 'materias'
                for index, m in enumerate(materias):
                    if m[0] == materia[0]:  # Comparar el id_materia
                        listboxMaterias.select_set(index)

            messagebox.showinfo("Carrera Encontrada", f"Carrera '{carrera[0]}' encontrada y campos llenados.")

        else:
            messagebox.showinfo("No Encontrada", "No se encontró una carrera con ese ID")

        conn.close()

    # Crear la ventana de administración de carreras y materias
    careerWindow = tk.Toplevel()
    careerWindow.title("Administración de Carreras")
    careerWindow.geometry("600x500")  # Ajustado el tamaño de la ventana para más espacio

    # Configuración de la cuadrícula
    careerWindow.grid_columnconfigure(0, weight=1)
    careerWindow.grid_columnconfigure(1, weight=3)

    # Sección de buscar carrera por ID
    tk.Label(careerWindow, text="Buscar Carrera por ID", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
    searchEntry = tk.Entry(careerWindow, font=("Arial", 10))
    searchEntry.grid(row=0, column=1, padx=10, pady=10)

    tk.Button(careerWindow, text="Buscar", font=("Arial", 10), command=buscar_carrera).grid(row=0, column=2, padx=10, pady=10)

    # Etiquetas y campos de entrada para ID y nombre de la carrera
    tk.Label(careerWindow, text="ID de la Carrera", font=("Arial", 10)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
    idEntry = tk.Entry(careerWindow, font=("Arial", 10))
    idEntry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(careerWindow, text="Nombre de la Carrera", font=("Arial", 10)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
    nameEntry = tk.Entry(careerWindow, font=("Arial", 10))
    nameEntry.grid(row=2, column=1, padx=10, pady=10)

    # Asignar materias a la carrera
    tk.Label(careerWindow, text="Seleccionar Materias", font=("Arial", 12)).grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="n")

    listboxMaterias = tk.Listbox(careerWindow, selectmode=MULTIPLE, height=8, font=("Arial", 10))
    listboxMaterias.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    # Cargar las materias en el listbox
    def cargar_materias():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_materia, nombre_materia FROM Materias")
        global materias
        materias = cursor.fetchall()  # Guardamos todas las materias en la variable global

        conn.close()

        listboxMaterias.delete(0, tk.END)

        for materia in materias:
            listboxMaterias.insert(tk.END, materia[1])  # Inserta solo el nombre de la materia

    cargar_materias()  # Llamamos a la función para cargar las materias al abrir la ventana

    # Botón de agregar carrera (ahora está abajo de la lista de materias)
    tk.Button(careerWindow, text="Agregar Carrera", font=("Arial", 12), command=agregar_carrera).grid(row=5, column=0, columnspan=2, padx=10, pady=20)

    careerWindow.mainloop()

# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("250x100")  # Ajuste para que la ventana principal sea más compacta

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", font=("Arial", 10), command=createCareerWindow).pack(padx=20, pady=20)

root.mainloop()
