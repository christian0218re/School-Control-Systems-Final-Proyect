from DataBase import conectar

# Función para iniciar sesión
def iniciar_sesion(correo, contra):
    print(correo)
    print(contra)
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id_usuario, nombre,tipo_usuario FROM Usuarios WHERE correo = ? AND contraseña = ?", (correo, contra))
    usuario = cursor.fetchone()
    conn.close()
    if usuario:
        return usuario  
    else:
        return None 

# Función para verificar permisos
def tiene_permiso(tipo_usuario, accion):
    permisos = {
        'administrador': ['all'],
        'maestro': ['ver_grupos', 'ver_materias', 'ver_alumnos'],
        'alumno': ['ver_materias', 'ver_horarios']
    }
    
    # Verifica si el tipo de usuario tiene permiso para realizar la acción
    return 'all' in permisos[tipo_usuario] or accion in permisos[tipo_usuario]
