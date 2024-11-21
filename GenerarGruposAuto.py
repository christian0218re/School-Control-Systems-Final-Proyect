import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from DataBase import conectar  # Importamos la función de conexión

def createGenerarGruposWindow():


    def generarGrupos():
        conexion = conectar()
        cursor = conexion.cursor()
        
        # Paso 1: Obtener todas las carreras
        cursor.execute("SELECT * FROM Carreras")
        carreras = cursor.fetchall()
        
        for carrera in carreras:
            print("Entro Carrera")
            id_carrera = carrera[0]
            
            # Paso 2: Obtener las materias asociadas a la carrera
            cursor.execute("""
                SELECT m.id_materia, m.nombre_materia FROM Materias m
                JOIN Materias_Carreras mc ON m.id_materia = mc.id_materia
                WHERE mc.id_carrera = ?
            """, (id_carrera,))
            materias = cursor.fetchall()

            for materia in materias:
                print("Entro Materia ", materia[0])
                id_materia = materia[0]
                
                # Paso 3: Verificar si hay entre 3 y 5 alumnos no asignados a esa materia para la carrera
                cursor.execute("""
                    SELECT COUNT(*) FROM Alumno_Materias am
                    JOIN Alumnos a ON am.id_alumno = a.id_alumno
                    WHERE am.id_materia = ? AND a.carrera = ? AND am.asignado = 0
                """, (id_materia, carrera[1]))
                count_alumnos = cursor.fetchone()[0]
                print(f"Alumnos no asignados para materia {id_materia} y carrera {carrera[1]}: {count_alumnos}")
                
                # Si no hay suficientes alumnos, saltamos a la siguiente materia
                if not (3 <= count_alumnos <= 5):
                    print(f"No hay suficientes alumnos disponibles para la materia {id_materia}")
                    continue  # Salta a la siguiente materia

                print("Alumnos en rango (3-5)")

                # Paso 4: Verificar que haya un maestro disponible
                cursor.execute("""
                    SELECT m.id_maestro, m.nombre FROM Maestros m
                    JOIN Maestro_Materias mm ON m.id_maestro = mm.id_maestro
                    WHERE mm.id_materia = ? AND m.id_maestro IN (
                        SELECT id_maestro FROM Maestro_Carreras WHERE id_carrera = ?
                    )
                """, (id_materia, id_carrera))
                
                maestros = cursor.fetchall()
                if not maestros:
                    print(f"No hay maestros disponibles para la materia {id_materia}")
                    continue  # Salta a la siguiente materia si no hay maestros
                    
                grupo_creado = False  # Variable para controlar si se creó el grupo
                
                for maestro in maestros:
                    if grupo_creado:  # Si ya se creó un grupo, salir del bucle de maestros
                        break
                        
                    print("Evaluando Maestro")
                    id_maestro = maestro[0]
                    
                    # Paso 5: Verificar horarios disponibles
                    cursor.execute("""
                        SELECT h.id_horario, h.turno, h.hora_inicio, h.hora_fin FROM Horarios h
                        WHERE h.id_horario NOT IN (
                            SELECT id_horario FROM Grupos WHERE id_maestro = ?
                        )
                    """, (id_maestro,))
                    horarios = cursor.fetchall()
                    
                    if not horarios:
                        print(f"No hay horarios disponibles para el maestro {id_maestro}")
                        continue  # Probar con el siguiente maestro
                    
                    for horario in horarios:
                        if grupo_creado:  # Si ya se creó un grupo, salir del bucle de horarios
                            break
                            
                        id_horario = horario[0]
                        print("Evaluando Horario")
                        
                        # Paso 6: Verificar salones disponibles
                        cursor.execute("""
                            SELECT id_salon, numero_salon FROM Salones
                            WHERE id_salon NOT IN (
                                SELECT id_salon FROM Grupos WHERE id_horario = ?
                            )
                        """, (id_horario,))
                        salones = cursor.fetchall()
                        
                        if not salones:
                            print(f"No hay salones disponibles para el horario {id_horario}")
                            continue  # Probar con el siguiente horario
                        
                        print("Creando grupo...")
                        try:
                                # Paso 7: Crear el grupo
                                fecha = '2024-11-21'
                                semestre = '2024-1'
                                max_alumnos = 5

                                cursor.execute("""
                                    INSERT INTO Grupos (fecha, id_carrera, id_materia, id_maestro, id_salon, id_horario, semestre, max_alumnos)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (fecha, id_carrera, id_materia, id_maestro, salones[0][0], id_horario, semestre, max_alumnos))
                                
                                # Obtener el ID del grupo recién creado
                                id_grupo = cursor.lastrowid

                                # Paso 8: Obtener los alumnos que serán asignados
                                cursor.execute("""
                                    SELECT id_alumno FROM Alumno_Materias 
                                    WHERE id_materia = ? AND asignado = 0
                                    LIMIT 5
                                """, (id_materia,))
                                alumnos_para_asignar = cursor.fetchall()

                                # Paso 9: Asignar los alumnos al grupo
                                for alumno in alumnos_para_asignar:
                                    id_alumno = alumno[0]
                                    # Insertar en la tabla Grupo_Alumnos
                                    cursor.execute("""
                                        INSERT INTO Grupo_Alumnos (id_grupo, id_alumno, fecha_asignacion)
                                        VALUES (?, ?, ?)
                                    """, (id_grupo, id_alumno, fecha))
                                    
                                    # Actualizar el estado de asignación en Alumno_Materias
                                    cursor.execute("""
                                        UPDATE Alumno_Materias 
                                        SET asignado = 1 
                                        WHERE id_materia = ? AND id_alumno = ?
                                    """, (id_materia, id_alumno))

                                    # Actualizar horarios ocupados del alumno
                                    cursor.execute("""
                                        UPDATE Alumnos
                                        SET horarios_ocupados = IFNULL(horarios_ocupados, '') || ? 
                                        WHERE id_alumno = ?
                                    """, (f"{horario[1]} {horario[2]} - {horario[3]}", id_alumno))

                                # Paso 10: Actualizar horarios del maestro
                                cursor.execute("""
                                    UPDATE Maestros
                                    SET horarios_ocupados = IFNULL(horarios_ocupados, '') || ?
                                    WHERE id_maestro = ?
                                """, (f"{horario[1]} {horario[2]} - {horario[3]}", id_maestro))

                                conexion.commit()
                                grupo_creado = True
                                messagebox.showinfo("Éxito", "Grupo generado y alumnos asignados exitosamente.")
                                
                                
                        except Exception as e:
                            print(f"Error al crear el grupo: {str(e)}")
                            conexion.rollback()
                            continue
        conexion.close()


    def eliminarGrupos():
        conexion = conectar()
        cursor = conexion.cursor()

        try:
            # Paso 1: Obtener todos los grupos para eliminar
            cursor.execute("""
                SELECT g.id_grupo, g.id_materia, g.id_maestro, g.id_horario, 
                    h.turno, h.hora_inicio, h.hora_fin
                FROM Grupos g
                JOIN Horarios h ON g.id_horario = h.id_horario
            """)
            grupos = cursor.fetchall()

            for grupo in grupos:
                id_grupo, id_materia, id_maestro, id_horario, turno, hora_inicio, hora_fin = grupo
                
                # Paso 2: Obtener los alumnos asignados al grupo
                cursor.execute("""
                    SELECT id_alumno 
                    FROM Grupo_Alumnos 
                    WHERE id_grupo = ?
                """, (id_grupo,))
                alumnos_asignados = cursor.fetchall()

                # Paso 3: Actualizar el estado de asignación de los alumnos
                for alumno in alumnos_asignados:
                    id_alumno = alumno[0]
                    
                    # Actualizar Alumno_Materias para marcar como no asignado
                    cursor.execute("""
                        UPDATE Alumno_Materias 
                        SET asignado = 0 
                        WHERE id_materia = ? AND id_alumno = ?
                    """, (id_materia, id_alumno))

                    # Eliminar el horario ocupado del alumno
                    cursor.execute("""
                        UPDATE Alumnos
                        SET horarios_ocupados = REPLACE(horarios_ocupados, ?, '')
                        WHERE id_alumno = ?
                    """, (f"{turno} {hora_inicio} - {hora_fin}", id_alumno))

                # Paso 4: Eliminar los horarios ocupados del maestro
                cursor.execute("""
                    UPDATE Maestros
                    SET horarios_ocupados = REPLACE(horarios_ocupados, ?, '')
                    WHERE id_maestro = ?
                """, (f"{turno} {hora_inicio} - {hora_fin}", id_maestro))

                # Paso 5: Eliminar las asignaciones de alumnos al grupo
                cursor.execute("""
                    DELETE FROM Grupo_Alumnos 
                    WHERE id_grupo = ?
                """, (id_grupo,))

                # Paso 6: Eliminar el grupo
                cursor.execute("""
                    DELETE FROM Grupos 
                    WHERE id_grupo = ?
                """, (id_grupo,))

            # Paso 7: Confirmar los cambios
            conexion.commit()
            messagebox.showinfo("Éxito", "Todos los grupos han sido eliminados correctamente.")

        except Exception as e:
            # En caso de error, deshacer cambios
            conexion.rollback()
            messagebox.showerror("Error", f"Ocurrió un error al eliminar los grupos: {str(e)}")
        
        finally:
            # Cerrar la conexión a la base de datos
            conexion.close()



    # Creación de la ventana
    grupoWindow = tk.Toplevel()
    grupoWindow.title("Administración de Grupos")
    grupoWindow.geometry("800x600")

    button_frame = tk.Frame(grupoWindow)
    button_frame.pack(expand=True)

    button_subframe = tk.Frame(button_frame)
    button_subframe.pack(anchor="center")

    tk.Button(button_subframe, text="Generar Grupos", font=("Arial", 12), command=generarGrupos).pack(pady=5)
    tk.Button(button_subframe, text="Elimar Grupos", font=("Arial", 12), command=eliminarGrupos).pack(pady=5)



# Llamada para abrir la ventana de administración de carreras desde la ventana principal
root = tk.Tk()
root.geometry("250x100")  # Ajuste para que la ventana principal sea más compacta

# Botón en la ventana principal para abrir la ventana de carreras
tk.Button(root, text="Abrir Ventana de Carreras", font=("Arial", 10), command=createGenerarGruposWindow).pack(padx=20, pady=20)

root.mainloop()
