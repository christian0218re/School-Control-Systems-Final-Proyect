import sqlite3

# Conexión a la base de datos
def conectar():
    conexion = sqlite3.connect('DataBase.db')
    return conexion

conexion = conectar()
cursor = conexion.cursor()

# Script de creación de tablas
script_sql = """
-- Creación de la tabla Usuarios
CREATE TABLE IF NOT EXISTS Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    a_paterno TEXT NOT NULL,
    a_materno TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    nombre_usuario TEXT NOT NULL,
    contraseña TEXT NOT NULL,
    tipo_usuario TEXT CHECK(tipo_usuario IN ('administrador', 'maestro', 'alumno')) NOT NULL
);

-- Creación de la tabla Carreras
CREATE TABLE IF NOT EXISTS Carreras (
    id_carrera INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_carrera TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Alumnos (
    id_alumno INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    fecha_nacimiento DATE,
    a_paterno TEXT,
    a_materno TEXT,
    carrera TEXT,
    estado TEXT,
    correo TEXT,
    id_usuario INTEGER NOT NULL, 
    horarios_ocupados TEXT, 
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de unión Alumno_Materias con columna asignado
CREATE TABLE IF NOT EXISTS Alumno_Materias (
    id_alumno INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    asignado INTEGER DEFAULT 0, 
    PRIMARY KEY (id_alumno, id_materia),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Maestros (
    id_maestro INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT ,
    a_paterno TEXT ,
    a_materno TEXT ,
    correo TEXT ,
    grado_estudio TEXT CHECK(grado_estudio IN ('Licenciatura', 'Maestria', 'Doctorado')) ,
    horarios_ocupados TEXT ,
    id_usuario INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de unión Maestro_Materias
CREATE TABLE IF NOT EXISTS Maestro_Materias (
    id_maestro INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    PRIMARY KEY (id_maestro, id_materia),
    FOREIGN KEY (id_maestro) REFERENCES Maestros(id_maestro),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia)
);

-- Tabla de unión Maestro_Carreras
CREATE TABLE IF NOT EXISTS Maestro_Carreras (
    id_maestro INTEGER NOT NULL,
    id_carrera INTEGER NOT NULL,
    PRIMARY KEY (id_maestro, id_carrera),
    FOREIGN KEY (id_maestro) REFERENCES Maestros(id_maestro),
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);


-- Creación de la tabla Materias
CREATE TABLE IF NOT EXISTS Materias (
    id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    codigo_materia TEXT UNIQUE NOT NULL,
    creditos INT,
    semestre TEXT
);

CREATE TABLE IF NOT EXISTS Materias_Carreras (
    id_materia INTEGER NOT NULL,
    id_carrera INTEGER NOT NULL,
    PRIMARY KEY (id_materia, id_carrera),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia),
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);

CREATE TABLE IF NOT EXISTS Horarios (
    id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
    turno TEXT CHECK(turno IN ('matutino', 'vespertino')) NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL
);

CREATE TABLE IF NOT EXISTS Grupos (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha DATE NOT NULL,
    id_carrera INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    id_maestro INTEGER NOT NULL,
    id_salon INTEGER NOT NULL,
    id_horario INTEGER NOT NULL,
    semestre TEXT NOT NULL,
    max_alumnos INTEGER NOT NULL,
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia),
    FOREIGN KEY (id_maestro) REFERENCES Maestros(id_maestro),
    FOREIGN KEY (id_salon) REFERENCES Salones(id_salon),
    FOREIGN KEY (id_horario) REFERENCES Horarios(id_horario)
);

-- Crear tabla de relación entre Grupos y Alumnos
CREATE TABLE IF NOT EXISTS Grupo_Alumnos (
    id_grupo_alumno INTEGER PRIMARY KEY AUTOINCREMENT,
    id_grupo INTEGER NOT NULL,
    id_alumno INTEGER NOT NULL,
    fecha_asignacion DATE NOT NULL,
    activo BOOLEAN DEFAULT 1,  -- Para manejar bajas temporales o definitivas
    FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno),
    -- Garantizar que un alumno no esté dos veces en el mismo grupo
    UNIQUE(id_grupo, id_alumno)
);

-- Crear índices para mejorar el rendimiento de las búsquedas
CREATE INDEX IF NOT EXISTS idx_grupo_alumnos_grupo ON Grupo_Alumnos(id_grupo);
CREATE INDEX IF NOT EXISTS idx_grupo_alumnos_alumno ON Grupo_Alumnos(id_alumno);

-- Creación de la tabla Salones
CREATE TABLE IF NOT EXISTS Salones (
    id_salon INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_salon TEXT UNIQUE NOT NULL,
    capacidad INTEGER NOT NULL,
    ubicacion TEXT
);

CREATE TABLE IF NOT EXISTS GrupoCreado (
    grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    Creado INTEGER DEFAULT 0

);

INSERT OR IGNORE INTO GrupoCreado (grupo, Creado) 
VALUES (1, 0);

"""
# Ejecutar el script SQL
cursor.executescript(script_sql)

#Para restablecer la base de datos descomenta todo lo de abajo pero primero elimina la DataBase.db
"""

def inicializarGrupoCreado():
    try:
        # Verificar si existe un registro con grupoid = 1
        cursor.execute("SELECT COUNT(*) FROM GrupoCreado WHERE grupo = 1")
        if cursor.fetchone()[0] == 0:
            # Crear el grupo inicial
            cursor.execute("INSERT INTO GrupoCreado (Creado) VALUES (0)")
            print("Grupo inicial creado con grupo = 1 y Creado = 0.")
        else:
            print("El grupo inicial ya existe.")
    except Exception as e:
        print(f"Error al inicializar el grupo: {e}")
    finally:
        pass

inicializarGrupoCreado()
# Salones predeterminados
salones = [
    ("A101", 30, "Primera planta"),
    ("B202", 40, "Segunda planta"),
    ("C303", 25, "Tercer piso"),
    ("D404", 50, "Edificio principal"),
    ("E505", 20, "Anexo A")
]

# Insertar salones si no existen
for numero_salon, capacidad, ubicacion in salones:
    cursor.execute("SELECT * FROM Salones WHERE numero_salon = ?", (numero_salon,))
    salon_existe = cursor.fetchone()
    if not salon_existe:
        cursor.execute("INSERT INTO Salones (numero_salon, capacidad, ubicacion) VALUES (?, ?, ?)", (numero_salon, capacidad, ubicacion))
        print(f"Salón '{numero_salon}' creado con éxito.")
        
# Datos para las tablas relacionadas
carrera = ("Computación",)
materias = [
    ("Matemáticas Discretas", "MAT101", 8, "1°"),
    ("Estructuras de Datos", "EST202", 10, "3°"),
    ("Redes de Computadoras", "RED303", 9, "5°"),
    ("Sistemas Operativos", "SIS404", 9, "5°"),
    ("Inteligencia Artificial", "IA505", 10, "7°")
]
maestros = [
    ("Juan", "Pérez", "García", "maestro1", "Doctorado"),
    ("Ana", "López", "Martínez", "maestro2", "Maestria"),
    ("Luis", "Hernández", "Sánchez", "maestro3", "Licenciatura"),
    ("María", "González", "Ramírez", "maestro4", "Doctorado"),
    ("Carlos", "Ramírez", "Torres", "maestro5", "Maestria")
]
alumnos = [
    ("Roberto", "Martínez", "López", "1995-06-15", "alumno1"),
    ("Laura", "Fernández", "García", "1996-08-20", "alumno2"),
    ("Pedro", "Sánchez", "Torres", "1994-02-10", "alumno3"),
    ("Mónica", "Castro", "Hernández", "1997-12-25", "alumno4"),
    ("José", "Rodríguez", "Pérez", "1998-05-18", "alumno5")
]
usuarios = [
    # Tipo usuario: administrador, maestro, alumno
    ("admin", "admin", "admin", "admin", "administrador", "", ""),
    ("Juan Pérez", "maestro1", "juan", "1234", "maestro", "Pérez", "Juan"),
    ("Ana López", "maestro2", "ana", "1234", "maestro", "López", "Ana"),
    ("Luis Hernández", "maestro3", "luis", "1234", "maestro", "Hernández", "Luis"),
    ("María González", "maestro4", "maria", "1234", "maestro", "González", "María"),
    ("Carlos Ramírez", "maestro5", "carlos", "1234", "maestro", "Ramírez", "Carlos"),
    ("Roberto Martínez", "alumno1", "roberto", "1234", "alumno", "Martínez", "Roberto"),
    ("Laura Fernández", "alumno2", "laura", "1234", "alumno", "Fernández", "Laura"),
    ("Pedro Sánchez", "alumno3", "pedro", "1234", "alumno", "Sánchez", "Pedro"),
    ("Mónica Castro", "alumno4", "monica", "1234", "alumno", "Castro", "Mónica"),
    ("José Rodríguez", "alumno5", "jose", "1234", "alumno", "Rodríguez", "José")
]

# Relación de materias con carrera
materias_carrera = [
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)  # Todas las materias pertenecen a la carrera 1
]

# Relación de maestros con carrera
maestros_carrera = [
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)  # Todos los maestros están en Computación
]
maestro_materias = [
    (1, 1), (1, 2),  # Juan enseña Matemáticas Discretas y Estructuras de Datos
    (2, 3), (2, 4),  # Ana enseña Redes de Computadoras y Sistemas Operativos
    (3, 5),          # Luis enseña Inteligencia Artificial
    (4, 1), (4, 4),  # María enseña Matemáticas Discretas y Sistemas Operativos
    (5, 2), (5, 5)   # Carlos enseña Estructuras de Datos e Inteligencia Artificial
]

# Relación alumnos-materias
alumnos_materias = [
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),  # Roberto tiene todas las materias
    (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),  # Laura tiene todas las materias
    (3, 1), (3, 2), (3, 3),                 # Pedro tiene 3 materias
    (4, 3), (4, 4), (4, 5),                 # Mónica tiene 3 materias
    (5, 1), (5, 2), (5, 3),          # José tiene 4 materias
]
horarios = [
    ('matutino', '07:00', '08:00'),
    ('matutino', '09:00', '10:00'),
    ('matutino', '10:00', '11:00'),
    ('matutino', '7:00', '10:00'),
    ('vespertino', '13:00', '14:00'),
    ('vespertino', '14:00', '15:00')
]

# Carreras
cursor.execute("INSERT INTO Carreras (nombre_carrera) VALUES (?)", carrera)

# Materias
for nombre, codigo, creditos, semestre in materias:
    cursor.execute("INSERT INTO Materias (nombre_materia, codigo_materia, creditos, semestre) VALUES (?, ?, ?, ?)", (nombre, codigo, creditos, semestre))

# Usuarios
for nombre, correo, usuario, contraseña, tipo, a_paterno, a_materno in usuarios:
    cursor.execute("INSERT INTO Usuarios (nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                   (nombre, a_paterno, a_materno, correo, usuario, contraseña, tipo))

for nombre, a_paterno, a_materno, correo, grado in maestros:
    cursor.execute("SELECT id_usuario FROM Usuarios WHERE correo = ?", (correo,))
    id_usuario = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO Maestros (nombre, a_paterno, a_materno, correo, grado_estudio, id_usuario) VALUES (?, ?, ?, ?, ?, ?)", 
                   (nombre, a_paterno, a_materno, correo, grado, id_usuario))

for nombre, a_paterno, a_materno, fecha, correo in alumnos:
    cursor.execute("SELECT id_usuario FROM Usuarios WHERE correo = ?", (correo,))
    id_usuario = cursor.fetchone()[0]
    
    cursor.execute("INSERT INTO Alumnos (nombre, a_paterno, a_materno, fecha_nacimiento, correo, carrera, estado, id_usuario) VALUES (?, ?, ?, ?, ?, ?, 'Activo', ?)", 
                  (nombre, a_paterno, a_materno, fecha, correo, "Computación", id_usuario))

# Relaciones Maestro-Carrera y Materias-Carrera
for id_maestro, id_carrera in maestros_carrera:
    cursor.execute("INSERT INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)", (id_maestro, id_carrera))

for id_materia, id_carrera in materias_carrera:
    cursor.execute("INSERT INTO Materias_Carreras (id_materia, id_carrera) VALUES (?, ?)", (id_materia, id_carrera))

# Insertar relaciones entre maestros y materias
for id_maestro, id_materia in maestro_materias:
    cursor.execute("INSERT INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)", (id_maestro, id_materia))
# Relación Alumnos-Materias
for id_alumno, id_materia in alumnos_materias:
    cursor.execute("INSERT INTO Alumno_Materias (id_alumno, id_materia) VALUES (?, ?)", (id_alumno, id_materia))
# Insertar horarios en la tabla
for turno, hora_inicio, hora_fin in horarios:
    cursor.execute("INSERT INTO Horarios (turno, hora_inicio, hora_fin) VALUES (?, ?, ?)", (turno, hora_inicio, hora_fin))
# Guardar cambios
conexion.commit()
print("Datos insertados correctamente.")

def mostrar_datos():
    # Consultar y mostrar los registros de las tablas
    cursor.execute("SELECT * FROM Carreras")
    print("Carreras:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Materias")
    print("\nMaterias:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Usuarios")
    print("\nUsuarios:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Maestros")
    print("\nMaestros:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Maestro_Materias")
    print("\nRelación Maestros-Materias:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Alumno_Materias")
    print("\nRelación Alumnos-Materias:")
    for fila in cursor.fetchall():
        print(fila)
"""
#mostrar_datos()
# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()
