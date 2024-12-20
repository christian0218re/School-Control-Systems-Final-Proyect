import tkinter as tk
from tkinter import ttk
import sqlite3
from DataBase import conectar

def createPlaneacionHorarioWindow(id_usuario):
    def cargar_grupos(id_usuario, filtro_carrera=None, filtro_materia=None):
        conn = conectar()
        cursor = conn.cursor()
        
        # Primero, determinar si el usuario es un maestro o un alumno
        cursor.execute("SELECT 'maestro' FROM Maestros WHERE id_usuario = ?", (id_usuario,))
        es_maestro = cursor.fetchone()
        
        if es_maestro:
            # Si es maestro, mostrar grupos que imparte
            query = """
            SELECT
            g.id_grupo, 
            c.nombre_carrera AS carrera, 
            m.nombre_materia AS materia,
            ma.nombre || ' ' || ma.a_paterno || ' ' || ma.a_materno AS maestro,
            s.numero_salon AS salon, 
            h.hora_inicio, 
            h.hora_fin, 
            h.turno,
            g.semestre, 
            g.max_alumnos,
            COUNT(CASE WHEN ga.activo = 1 THEN 1 END) as alumnos_inscritos
            FROM Grupos g
            JOIN Carreras c ON g.id_carrera = c.id_carrera
            JOIN Materias m ON g.id_materia = m.id_materia
            JOIN Maestros ma ON g.id_maestro = ma.id_maestro
            JOIN Salones s ON g.id_salon = s.id_salon
            JOIN Horarios h ON g.id_horario = h.id_horario
            LEFT JOIN Grupo_Alumnos ga ON g.id_grupo = ga.id_grupo
            WHERE ma.id_usuario = ?
            GROUP BY 
                g.id_grupo, 
                c.nombre_carrera, 
                m.nombre_materia, 
                ma.nombre, 
                ma.a_paterno, 
                ma.a_materno,
                s.numero_salon, 
                h.hora_inicio, 
                h.hora_fin, 
                h.turno,
                g.semestre, 
                g.max_alumnos
            ORDER BY h.hora_inicio ASC, h.turno ASC
            """
            params = [id_usuario]
        else:
            # Si es alumno, mostrar grupos en los que está inscrito
            query = """
            SELECT 
                g.id_grupo, c.nombre_carrera AS carrera, m.nombre_materia AS materia, 
                ma.nombre || ' ' || ma.a_paterno || ' ' || ma.a_materno AS maestro,
                s.numero_salon AS salon, h.hora_inicio, h.hora_fin, h.turno, 
                g.semestre, g.max_alumnos,
                COUNT(CASE WHEN ga.activo = 1 THEN 1 END) as alumnos_inscritos
            FROM Grupos g
            JOIN Carreras c ON g.id_carrera = c.id_carrera
            JOIN Materias m ON g.id_materia = m.id_materia
            JOIN Maestros ma ON g.id_maestro = ma.id_maestro
            JOIN Salones s ON g.id_salon = s.id_salon
            JOIN Horarios h ON g.id_horario = h.id_horario
            JOIN Grupo_Alumnos ga ON g.id_grupo = ga.id_grupo
            JOIN Alumnos a ON ga.id_alumno = a.id_alumno
            WHERE a.id_usuario = ? AND ga.activo = 1
            """
            params = [id_usuario]
        
        # Aplicar filtros adicionales si están presentes
        if filtro_carrera:
            query += " AND c.nombre_carrera = ?"
            params.append(filtro_carrera)
        if filtro_materia:
            query += " AND m.nombre_materia = ?"
            params.append(filtro_materia)
        
        query += " GROUP BY g.id_grupo ORDER BY h.hora_inicio ASC, h.turno ASC"
        
        cursor.execute(query, params)
        grupos = cursor.fetchall()
        conn.close()
        return grupos

    def cargar_carreras_y_materias():
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT nombre_carrera FROM Carreras")
        carreras = [fila[0] for fila in cursor.fetchall()]

        cursor.execute("SELECT nombre_materia FROM Materias")
        materias = [fila[0] for fila in cursor.fetchall()]

        conn.close()
        return carreras, materias

    def actualizar_vista():
        for widget in frame_grupos.winfo_children():
            widget.destroy()
        
        grupos = cargar_grupos(id_usuario, combo_carrera.get(), combo_materia.get())
        
        # Crear un marco principal para contener los grupos
        marco_principal = tk.Frame(frame_grupos)
        marco_principal.pack(fill="both", expand=True)
        
        # Iterar sobre los grupos de 3 en 3
        for i in range(0, len(grupos), 3):
            # Crear un marco para la fila de grupos
            fila_grupos = tk.Frame(marco_principal)
            fila_grupos.pack(fill="x", pady=5)
            
            # Obtener los grupos para esta fila (máximo 3)
            grupos_fila = grupos[i:i+3]
            
            # Crear tarjetas para los grupos en esta fila
            for j, grupo in enumerate(grupos_fila):
                id_grupo, carrera, materia, maestro, salon, hora_inicio, hora_fin, turno, semestre, max_alumnos, alumnos_inscritos = grupo
                
                # Crear un Frame para cada grupo
                card = tk.Frame(fila_grupos, bg="lightblue", bd=2, relief="solid", padx=10, pady=10)
                card.pack(side="left", padx=5, expand=True, fill="both")

                # Mostrar detalles del grupo
                tk.Label(card, text=f"Grupo ID: X{id_grupo}", font=("Arial", 12, "bold"), bg="lightblue").grid(row=0, column=0, sticky="w")
                tk.Label(card, text=f"Carrera: {carrera}", bg="lightblue").grid(row=1, column=0, sticky="w")
                tk.Label(card, text=f"Materia: {materia}", bg="lightblue").grid(row=2, column=0, sticky="w")
                tk.Label(card, text=f"Maestro: {maestro}", bg="lightblue").grid(row=3, column=0, sticky="w")
                tk.Label(card, text=f"Salón: {salon}", bg="lightblue").grid(row=4, column=0, sticky="w")
                tk.Label(card, text=f"Horario: {turno} {hora_inicio}-{hora_fin}", bg="lightblue").grid(row=5, column=0, sticky="w")
                tk.Label(card, text=f"Semestre: {semestre}", bg="lightblue").grid(row=6, column=0, sticky="w")
                
                # Agregar información de alumnos con porcentaje de ocupación
                ocupacion = (alumnos_inscritos / max_alumnos * 100) if max_alumnos > 0 else 0
                color = "green" if ocupacion < 80 else "orange" if ocupacion < 100 else "red"
                
                tk.Label(card, 
                        text=f"Alumnos: {alumnos_inscritos}/{max_alumnos} ({ocupacion:.1f}%)", 
                        bg="lightblue", 
                        fg=color, 
                        font=("Arial", 10, "bold")).grid(row=7, column=0, sticky="w")

    # Crear la ventana principal
    root = tk.Tk()
    root.title("Planeación de Grupos")

    # Filtros
    frame_filtros = tk.Frame(root, pady=10)
    frame_filtros.pack(fill="x")

    carreras, materias = cargar_carreras_y_materias()

    # Crear el combobox de carrera
    tk.Label(frame_filtros, text="Filtrar por Carrera:").pack(side="left", padx=5)
    combo_carrera = ttk.Combobox(frame_filtros, values=[""] + carreras)  
    combo_carrera.pack(side="left", padx=5)

    # Crear el combobox de materia con búsqueda dinámica
    tk.Label(frame_filtros, text="Filtrar por Materia:").pack(side="left", padx=5)
    combo_materia = ttk.Combobox(frame_filtros, values=[""] + materias) 
    combo_materia.pack(side="left", padx=5)

    def filtrar_materias(event):
        search_term = combo_materia.get().lower()  
        filtered_materias = [materia for materia in materias if search_term in materia.lower()]
        combo_materia['values'] = [""] + filtered_materias  

    def filtrar_carreras(event):
        search_term = combo_carrera.get().lower()  
        filtered_carreras = [carrera for carrera in carreras if search_term in carrera.lower()]
        combo_carrera['values'] = [""] + filtered_carreras 

    # Asociar el evento de key release para filtrar las materias
    combo_materia.bind("<KeyRelease>", filtrar_materias)
    combo_carrera.bind("<KeyRelease>", filtrar_carreras)

    btn_filtrar = tk.Button(frame_filtros, text="Filtrar", command=actualizar_vista)
    btn_filtrar.pack(side="left", padx=5)

    # Scrollable Frame para los grupos
    frame_scroll = tk.Frame(root)
    frame_scroll.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame_scroll)
    scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    frame_grupos = scrollable_frame

    # Cargar datos iniciales
    actualizar_vista()

    root.mainloop()