import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from DataBase import conectar  # Asegúrate de que esta función está en tu archivo DataBase

def createGrupoWindow():
    # Funciones principales (vacías por ahora)
    def buscar_grupo():
        pass

    def agregar_grupo():
        pass

    def editar_grupo():
        pass

    def eliminar_grupo():
        pass

    def limpiar_campos():
        pass

    def nuevo():
        pass

    def cancelar():
        pass

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
    fechaEntry = tk.Entry(details_frame, font=("Arial", 10))
    fechaEntry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

    # Combobox para Carrera, Maestro, Materia
    tk.Label(details_frame, text="Carrera:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    carrera_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    carrera_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Maestro:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    maestro_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    maestro_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Materia:", font=("Arial", 10)).grid(row=4, column=0, sticky="e", padx=5, pady=5)
    materia_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    materia_combobox.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    # Combobox para Salón y Horario
    tk.Label(details_frame, text="Salón:", font=("Arial", 10)).grid(row=5, column=0, sticky="e", padx=5, pady=5)
    salon_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    salon_combobox.grid(row=5, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Horario:", font=("Arial", 10)).grid(row=6, column=0, sticky="e", padx=5, pady=5)
    horario_combobox = ttk.Combobox(details_frame, font=("Arial", 10), state="readonly")
    horario_combobox.grid(row=6, column=1, padx=5, pady=5, sticky="ew")

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




# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("250x100")  # Ajuste para que la ventana principal sea más compacta

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", font=("Arial", 10), command=createGrupoWindow).pack(padx=20, pady=20)

root.mainloop()