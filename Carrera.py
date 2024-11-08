import tkinter as tk
from tkinter import messagebox, MULTIPLE
from tkinter import ttk
from DataBase import conectar  # Función de conexión a la base de datos

materias = None  # Variable global para almacenar materias desde la base de datos

def createCareerWindow():
    # Agregar una carrera y asociarla con materias seleccionadas
    def agregar_carrera():
        conn = conectar()
        cursor = conn.cursor()

        id_carrera = idEntry.get()
        nombre = nameEntry.get()

        # Validación de datos necesarios
        if not nombre:
            messagebox.showinfo("Error", "Por favor rellene el campo de nombre de carrera")
            return

        materias_seleccionadas = listboxMaterias.curselection()
        if not materias_seleccionadas:
            messagebox.showinfo("Error", "Por favor seleccione al menos una materia")
            return

        try:
            # Insertar carrera en la base de datos
            cursor.execute("INSERT INTO Carreras (id_carrera, nombre_carrera) VALUES (?, ?)", (id_carrera, nombre))
            conn.commit()

            # Asignar materias seleccionadas a la carrera
            for materia_index in materias_seleccionadas:
                materia_id = materias[materia_index][0]
                cursor.execute("INSERT INTO Materias_Carreras (id_carrera, id_materia) VALUES (?, ?)", (id_carrera, materia_id))

            conn.commit()
            messagebox.showinfo("Éxito", "Carrera y materias agregadas correctamente")
            limpiar_campos()

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Limpiar los campos de entrada en la ventana
    def limpiar_campos():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        listboxMaterias.selection_clear(0, tk.END)

    # Buscar y rellenar los datos de una carrera existente en la interfaz
    def buscar_carrera():
        conn = conectar()
        cursor = conn.cursor()
        carrera_id = searchEntry.get()

        if not carrera_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de carrera")
            return

        # Consultar la base de datos para obtener detalles de la carrera
        cursor.execute("SELECT nombre_carrera FROM Carreras WHERE id_carrera = ?", (carrera_id,))
        carrera = cursor.fetchone()

        if carrera:
            # Rellenar campos con los datos de la carrera obtenida
            idEntry.delete(0, tk.END)
            idEntry.insert(tk.END, carrera_id)
            nameEntry.delete(0, tk.END)
            nameEntry.insert(tk.END, carrera[0])

            # Consultar las materias asociadas a la carrera
            cursor.execute("""
                SELECT m.id_materia, m.nombre_materia 
                FROM Materias m
                JOIN Materias_Carreras mc ON m.id_materia = mc.id_materia
                WHERE mc.id_carrera = ?
            """, (carrera_id,))
            materias_asociadas = cursor.fetchall()

            listboxMaterias.selection_clear(0, tk.END)

            # Ordenar y seleccionar materias
            materias_no_seleccionadas = []
            materias_seleccionadas = []
            for materia in materias:
                if materia[0] in [m[0] for m in materias_asociadas]:
                    materias_seleccionadas.append(materia)
                else:
                    materias_no_seleccionadas.append(materia)

            listboxMaterias.delete(0, tk.END)
            for materia in materias_seleccionadas + materias_no_seleccionadas:
                listboxMaterias.insert(tk.END, materia[1])

            for index, materia in enumerate(materias_seleccionadas + materias_no_seleccionadas):
                if materia in materias_seleccionadas:
                    listboxMaterias.select_set(index)

            messagebox.showinfo("Carrera Encontrada", f"Carrera '{carrera[0]}' encontrada y campos llenados.")
        else:
            messagebox.showinfo("No Encontrada", "No se encontró una carrera con ese ID")

        conn.close()

    # Función para editar los detalles de una carrera existente
    def editar_carrera():
        conn = conectar()
        cursor = conn.cursor()

        id_carrera = idEntry.get()
        nombre_nuevo = nameEntry.get()
        
        if not nombre_nuevo:
            messagebox.showinfo("Error", "Por favor rellene el campo de nombre de carrera")
            return

        materias_seleccionadas = listboxMaterias.curselection()
        if not materias_seleccionadas:
            messagebox.showinfo("Error", "Por favor seleccione al menos una materia")
            return

        try:
            # Actualizar nombre de carrera y materias
            cursor.execute("UPDATE Carreras SET nombre_carrera = ? WHERE id_carrera = ?", (nombre_nuevo, id_carrera))
            cursor.execute("DELETE FROM Materias_Carreras WHERE id_carrera = ?", (id_carrera,))
            for materia_index in materias_seleccionadas:
                materia_id = materias[materia_index][0]
                cursor.execute("INSERT INTO Materias_Carreras (id_carrera, id_materia) VALUES (?, ?)", (id_carrera, materia_id))

            conn.commit()
            cancelar()
            messagebox.showinfo("Éxito", "Carrera y materias actualizadas correctamente")

        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Eliminar una carrera y sus relaciones con materias de la base de datos
    def eliminar_carrera():
        conn = conectar()
        cursor = conn.cursor()

        id_carrera = idEntry.get()
        if not id_carrera:
            messagebox.showinfo("Error", "Por favor busque una carrera para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar esta carrera y sus materias asociadas?")
        if not confirmacion:
            return

        try:
            # Borrar carrera y relaciones
            cursor.execute("DELETE FROM Materias_Carreras WHERE id_carrera = ?", (id_carrera,))
            cursor.execute("DELETE FROM Carreras WHERE id_carrera = ?", (id_carrera,))
            conn.commit()
            messagebox.showinfo("Éxito", "Carrera y sus materias asociadas eliminadas correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()


    # Crear ventana de administración de carreras y materias
    careerWindow = tk.Toplevel()
    careerWindow.title("Administración de Carreras")
    careerWindow.geometry("600x500")

    # Configuración de la cuadrícula principal
    careerWindow.grid_columnconfigure(0, weight=1)
    careerWindow.grid_columnconfigure(1, weight=3)

    # Frame para búsqueda de carrera
    search_frame = ttk.LabelFrame(careerWindow, text="Buscar Carrera", padding="10")
    search_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    search_frame.grid_columnconfigure(1, weight=1)

    # Entrada y botón para buscar carrera por ID
    tk.Label(search_frame, text="ID:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    searchEntry = tk.Entry(search_frame, font=("Arial", 10))
    searchEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(search_frame, text="Buscar", font=("Arial", 10), command=buscar_carrera).grid(row=0, column=2, padx=5, pady=5)

    # Frame para detalles de la carrera
    details_frame = ttk.LabelFrame(careerWindow, text="Detalles de Carrera", padding="10")
    details_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    details_frame.grid_columnconfigure(1, weight=1)

    # Campos de entrada para ID y nombre de la carrera
    tk.Label(details_frame, text="ID de la Carrera:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    idEntry = tk.Entry(details_frame, font=("Arial", 10))
    idEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Nombre de la Carrera:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    nameEntry = tk.Entry(details_frame, font=("Arial", 10))
    nameEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Frame para selección de materias
    materia_frame = ttk.LabelFrame(careerWindow, text="Seleccionar Materias", padding="10")
    materia_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    materia_frame.grid_columnconfigure(1, weight=1)

    # Entrada y botón para buscar materias
    tk.Label(materia_frame, text="Buscar Materias:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=5, pady=5)
    materia_search_entry = tk.Entry(materia_frame, font=("Arial", 10))
    materia_search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    materia_search_button = tk.Button(materia_frame, text="Buscar", font=("Arial", 10), command=lambda: buscar_materias())
    materia_search_button.grid(row=0, column=2, padx=5, pady=5)

    # Listbox y Scrollbar en un frame
    listbox_frame = ttk.Frame(materia_frame)
    listbox_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")
    listbox_frame.grid_rowconfigure(0, weight=1)
    listbox_frame.grid_columnconfigure(0, weight=1)

    # Listbox para materias
    listboxMaterias = tk.Listbox(listbox_frame, selectmode=MULTIPLE, height=8, font=("Arial", 10))
    listboxMaterias.grid(row=0, column=0, sticky="nsew")

    # Scrollbar para el Listbox
    materia_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listboxMaterias.yview)
    materia_scrollbar.grid(row=0, column=1, sticky="ns")
    listboxMaterias.config(yscrollcommand=materia_scrollbar.set)

    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_carrera FROM Carreras ORDER BY id_carrera")
        ids_existentes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        # Encontrar el primer ID faltante en la secuencia
        siguiente_id = 1
        for id_ in ids_existentes:
            if id_ == siguiente_id:
                siguiente_id += 1
            else:
                break
        return siguiente_id

    def nuevo():
        limpiar_campos()
        idEntry.insert(0, obtener_siguiente_id())

    def cancelar():
        limpiar_campos()

    # Frame para botones de acciones de carrera
    button_frame = tk.Frame(careerWindow)
    button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

    # Subframe para centrar los botones dentro de button_frame
    button_subframe = tk.Frame(button_frame)
    button_subframe.pack(anchor="center")

    # Botones de acciones
    tk.Button(button_subframe, text="Nuevo", font=("Arial", 12), command=nuevo).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Agregar", font=("Arial", 12), command=agregar_carrera).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Cancelar", font=("Arial", 12), command=cancelar).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Editar", font=("Arial", 12), command=editar_carrera).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Baja", font=("Arial", 12), command=eliminar_carrera).pack(side="left", padx=5)




    # Función para cargar las materias en el Listbox
    def cargar_materias():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_materia, nombre_materia FROM Materias")
        global materias
        materias = cursor.fetchall()
        conn.close()
        
        listboxMaterias.delete(0, tk.END)
        for materia in materias:
            listboxMaterias.insert(tk.END, materia[1])

    cargar_materias()

    # Función para buscar materias
    def buscar_materias():
        materia_search_text = materia_search_entry.get()
        listboxMaterias.delete(0, tk.END)
        if materia_search_text:
            for materia in materias:
                if materia_search_text.lower() in materia[1].lower():
                    listboxMaterias.insert(tk.END, materia[1])
        else:
            for materia in materias:
                listboxMaterias.insert(tk.END, materia[1])

    careerWindow.mainloop()

'''
# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("250x100")  # Ajuste para que la ventana principal sea más compacta

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", font=("Arial", 10), command=createCareerWindow).pack(padx=20, pady=20)

root.mainloop()'''