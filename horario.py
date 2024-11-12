import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from DataBase import conectar  # Función de conexión a la base de datos

def createHorarioWindow():

    def es_hora_valida(turno, hora_inicio):
        """Valida si la hora de inicio es correcta según el turno."""
        inicio_hora = int(hora_inicio.split(":")[0])
        if turno == "matutino" and 7 <= inicio_hora <= 12:
            return True
        elif turno == "vespertino" and 13 <= inicio_hora <= 20:
            return True
        return False
    # Agregar un nuevo horario
    def agregar_horario():
        conn = conectar()
        cursor = conn.cursor()

        id_horario = idEntry.get()        
        turno = turno_combobox.get()
        hora_inicio = horaInicio_combobox.get()
        hora_fin = horaFin_combobox.get()

        # Validación de campos vacíos
        if not turno or not hora_inicio or not hora_fin:
            messagebox.showinfo("Error", "Por favor rellene todos los campos de horario")
            return

        # Validación de hora de inicio para el turno
        if not es_hora_valida(turno, hora_inicio):
            messagebox.showinfo("Error", f"La hora de inicio {hora_inicio} no es válida para el turno {turno}")
            return

        # Validación de que la hora de inicio no sea mayor o igual a la hora de fin
        if int(hora_inicio.split(":")[0]) >= int(hora_fin.split(":")[0]):
            messagebox.showinfo("Error", "La hora de inicio no puede ser mayor o igual que la hora de fin")
            return
        hora_inicio_horas = int(hora_inicio.split(":")[0])
        hora_fin_horas = int(hora_fin.split(":")[0])
        # Validación de que hora de inicio y hora de fin sean maximos 4 horas
        if (hora_fin_horas - hora_inicio_horas) > 4:
            messagebox.showinfo("Error", f"La diferencia entre la hora de inicio ({hora_inicio}) y la hora de fin ({hora_fin}) no puede ser mayor a 4 horas.")
            return

        try:
            cursor.execute("INSERT INTO Horarios (id_horario, turno, hora_inicio, hora_fin) VALUES (?, ?, ?, ?)",
                           (id_horario, turno, hora_inicio, hora_fin))
            conn.commit()
            messagebox.showinfo("Éxito", "Horario agregado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Limpiar los campos de entrada en la ventana
    def limpiar_campos():
        idEntry.config(state="normal")
        searchEntry.delete(0,tk.END)
        idEntry.delete(0, tk.END)  
        turno_combobox.set("")     
        horaInicio_combobox.set("")  
        horaFin_combobox.set("")   

    # Buscar y rellenar los datos de un horario existente en la interfaz
    def buscar_horario():
        conn = conectar()
        cursor = conn.cursor()
        horario_id = searchEntry.get()

        if not horario_id:
            messagebox.showinfo("Error", "Por favor ingrese un ID de horario")
            return

        cursor.execute("SELECT turno, hora_inicio, hora_fin FROM Horarios WHERE id_horario = ?", (horario_id,))
        horario = cursor.fetchone()

        if horario:
            idEntry.delete(0, tk.END)  
            idEntry.insert(tk.END, horario_id)
            idEntry.config(state="disabled")

            turno_combobox.set(horario[0]) 

            horaInicio_combobox.set(horario[1])  
            horaFin_combobox.set(horario[2]) 

            messagebox.showinfo("Horario Encontrado", f"Horario '{horario_id}' encontrado y campos llenados.")
        else:
            messagebox.showinfo("No Encontrado", "No se encontró un horario con ese ID")

        conn.close()

    def editar_horario():
        conn = conectar()
        cursor = conn.cursor()

        id_horario = idEntry.get()
        turno = turno_combobox.get()
        hora_inicio = horaInicio_combobox.get()
        hora_fin = horaFin_combobox.get()

        # Validación de campos vacíos
        if not turno or not hora_inicio or not hora_fin:
            messagebox.showinfo("Error", "Por favor rellene todos los campos de horario")
            return

        # Validación de hora de inicio para el turno
        if not es_hora_valida(turno, hora_inicio):
            messagebox.showinfo("Error", f"La hora de inicio {hora_inicio} no es válida para el turno {turno}")
            return

        # Validación de que la hora de inicio no sea mayor o igual a la hora de fin
        if int(hora_inicio.split(":")[0]) >= int(hora_fin.split(":")[0]):
            messagebox.showinfo("Error", "La hora de inicio no puede ser mayor o igual que la hora de fin")
            return

        hora_inicio_horas = int(hora_inicio.split(":")[0])
        hora_fin_horas = int(hora_fin.split(":")[0])
        # Validación de que hora de inicio y hora de fin sean maximos 4 horas
        if (hora_fin_horas - hora_inicio_horas) > 4:
            messagebox.showinfo("Error", f"La diferencia entre la hora de inicio ({hora_inicio}) y la hora de fin ({hora_fin}) no puede ser mayor a 4 horas.")
            return


        try:
            cursor.execute("UPDATE Horarios SET turno = ?, hora_inicio = ?, hora_fin = ? WHERE id_horario = ?",
                           (turno, hora_inicio, hora_fin, id_horario))
            conn.commit()
            cancelar()
            messagebox.showinfo("Éxito", "Horario actualizado correctamente")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Eliminar un horario de la base de datos
    def eliminar_horario():
        conn = conectar()
        cursor = conn.cursor()

        id_horario = idEntry.get()
        if not id_horario:
            messagebox.showinfo("Error", "Por favor busque un horario para eliminar")
            return

        confirmacion = messagebox.askyesno("Confirmación", "¿Estás seguro de que deseas eliminar este horario?")
        if not confirmacion:
            return

        try:
            cursor.execute("DELETE FROM Horarios WHERE id_horario = ?", (id_horario,))
            conn.commit()
            messagebox.showinfo("Éxito", "Horario eliminado correctamente")
            limpiar_campos()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Crear ventana de administración de horarios
    horarioWindow = tk.Toplevel()
    horarioWindow.title("Administración de Horarios")
    horarioWindow.geometry("600x400")

    # Frame para búsqueda de horario
    search_frame = ttk.LabelFrame(horarioWindow, text="Buscar Horario", padding="10")
    search_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
    searchEntry = tk.Entry(search_frame, font=("Arial", 10))
    searchEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
    tk.Button(search_frame, text="Buscar", font=("Arial", 10), command=buscar_horario).grid(row=0, column=2, padx=5, pady=5)

    # Frame para detalles del horario
    details_frame = ttk.LabelFrame(horarioWindow, text="Detalles de Horario", padding="10")
    details_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")

    # Campos de entrada para ID y detalles del horario
    tk.Label(details_frame, text="ID del Horario:", font=("Arial", 10)).grid(row=0, column=0, sticky="e", padx=5, pady=5)
    idEntry = tk.Entry(details_frame, font=("Arial", 10))
    idEntry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    tk.Label(details_frame, text="Turno:", font=("Arial", 10)).grid(row=1, column=0, sticky="e", padx=5, pady=5)
    turno_options = ["matutino", "vespertino"]
    turno_combobox = ttk.Combobox(details_frame, values=turno_options, font=("Arial", 10), state="readonly")
    turno_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")


    horas_inicio_opciones = [f"{h:02d}:00" for h in range(7, 21)]
    horas_fin_opciones = [f"{h:02d}:00" for h in range(8, 22)]

    # Label y Combobox para "Hora Inicio"
    tk.Label(details_frame, text="Hora Inicio:", font=("Arial", 10)).grid(row=2, column=0, sticky="e", padx=5, pady=5)
    horaInicio_combobox = ttk.Combobox(details_frame, values=horas_inicio_opciones, font=("Arial", 10), state="readonly")
    horaInicio_combobox.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

    # Label y Combobox para "Hora Fin"
    tk.Label(details_frame, text="Hora Fin:", font=("Arial", 10)).grid(row=3, column=0, sticky="e", padx=5, pady=5)
    horaFin_combobox = ttk.Combobox(details_frame, values=horas_fin_opciones, font=("Arial", 10), state="readonly")
    horaFin_combobox.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

    # Función para obtener el próximo ID
    def obtener_siguiente_id():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT id_horario FROM Horarios ORDER BY id_horario")
        ids_existentes = [row[0] for row in cursor.fetchall()]
        conn.close()
        
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

    # Frame para botones de acciones
    button_frame = tk.Frame(horarioWindow)
    button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

    # Subframe para centrar los botones
    button_subframe = tk.Frame(button_frame)
    button_subframe.pack(anchor="center")

    # Botones de acciones
    tk.Button(button_subframe, text="Nuevo", font=("Arial", 12), command=nuevo).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Agregar", font=("Arial", 12), command=agregar_horario).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Cancelar", font=("Arial", 12), command=cancelar).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Editar", font=("Arial", 12), command=editar_horario).pack(side="left", padx=5)
    tk.Button(button_subframe, text="Baja", font=("Arial", 12), command=eliminar_horario).pack(side="left", padx=5)
