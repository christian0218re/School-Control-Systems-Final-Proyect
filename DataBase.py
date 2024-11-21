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

-- Creación de la tabla Alumnos
CREATE TABLE IF NOT EXISTS Alumnos (
    id_alumno INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT,
    fecha_nacimiento DATE,
    a_paterno TEXT,
    a_materno TEXT,
    carrera TEXT,
    estado TEXT,
    correo TEXT,
    id_usuario INTEGER NOT NULL, -- Campo que referencia a Usuarios
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de unión Alumno_Materias
CREATE TABLE IF NOT EXISTS Alumno_Materias (
    id_alumno INTEGER NOT NULL,
    id_materia INTEGER NOT NULL,
    PRIMARY KEY (id_alumno, id_materia),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS Maestros (
    id_maestro INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    a_paterno TEXT NOT NULL,
    a_materno TEXT NOT NULL,
    correo TEXT NOT NULL,
    grado_estudio TEXT CHECK(grado_estudio IN ('Licenciatura', 'Maestria', 'Doctorado')) NOT NULL
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


CREATE TABLE IF NOT EXISTS Grupo_Alumnos (
    id_grupo INTEGER NOT NULL,
    id_alumno INTEGER NOT NULL,
    PRIMARY KEY (id_grupo, id_alumno),
    FOREIGN KEY (id_grupo) REFERENCES Grupos(id_grupo) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Creación de la tabla Salones
CREATE TABLE IF NOT EXISTS Salones (
    id_salon INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_salon TEXT UNIQUE NOT NULL,
    capacidad INTEGER NOT NULL,
    ubicacion TEXT
);

"""
# Ejecutar el script SQL
cursor.executescript(script_sql)
"""
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
    ("Juan", "Pérez", "García", "juan.perez@example.com", "Doctorado"),
    ("Ana", "López", "Martínez", "ana.lopez@example.com", "Maestria"),
    ("Luis", "Hernández", "Sánchez", "luis.hernandez@example.com", "Licenciatura"),
    ("María", "González", "Ramírez", "maria.gonzalez@example.com", "Doctorado"),
    ("Carlos", "Ramírez", "Torres", "carlos.ramirez@example.com", "Maestria")
]
alumnos = [
    ("Roberto", "Martínez", "López", "1995-06-15", "computacion1@example.com"),
    ("Laura", "Fernández", "García", "1996-08-20", "computacion2@example.com"),
    ("Pedro", "Sánchez", "Torres", "1994-02-10", "computacion3@example.com"),
    ("Mónica", "Castro", "Hernández", "1997-12-25", "computacion4@example.com"),
    ("José", "Rodríguez", "Pérez", "1998-05-18", "computacion5@example.com")
]
usuarios = [
    # Tipo usuario: administrador, maestro, alumno
    ("admin", "admin", "admin", "admin", "administrador", "", ""),  # Sin apellidos
    ("Juan Pérez", "juan.perez@example.com", "juan", "1234", "maestro", "Pérez", "Juan"),
    ("Ana López", "ana.lopez@example.com", "ana", "1234", "maestro", "López", "Ana"),
    ("Luis Hernández", "luis.hernandez@example.com", "luis", "1234", "maestro", "Hernández", "Luis"),
    ("Roberto Martínez", "computacion1@example.com", "roberto", "1234", "alumno", "Martínez", "Roberto"),
    ("Laura Fernández", "computacion2@example.com", "laura", "1234", "alumno", "Fernández", "Laura"),
    ("Pedro Sánchez", "computacion3@example.com", "pedro", "1234", "alumno", "Sánchez", "Pedro")
]

# Relación de materias con carrera
materias_carrera = [
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)  # Todas las materias pertenecen a la carrera 1
]

# Relación de maestros con carrera
maestros_carrera = [
    (1, 1), (2, 1), (3, 1), (4, 1), (5, 1)  # Todos los maestros están en Computación
]

# Relación alumnos-materias
alumnos_materias = [
    (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),  # Roberto tiene todas las materias
    (2, 1), (2, 2), (2, 3), (2, 4), (2, 5),  # Laura tiene todas las materias
    (3, 1), (3, 2), (3, 3),                 # Pedro tiene 3 materias
    (4, 3), (4, 4), (4, 5),                 # Mónica tiene 3 materias
    (5, 1), (5, 2), (5, 4), (5, 5)          # José tiene 4 materias
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
# Maestros
for nombre, a_paterno, a_materno, correo, grado in maestros:
    cursor.execute("INSERT INTO Maestros (nombre, a_paterno, a_materno, correo, grado_estudio) VALUES (?, ?, ?, ?, ?)", (nombre, a_paterno, a_materno, correo, grado))

# Alumnos
for nombre, a_paterno, a_materno, fecha, correo in alumnos:
    cursor.execute("INSERT INTO Alumnos (nombre, a_paterno, a_materno, fecha_nacimiento, correo, carrera, estado, id_usuario) VALUES (?, ?, ?, ?, ?, ?, 'Activo', ?)", 
                  (nombre, a_paterno, a_materno, fecha, correo, "Computación", 1))

# Relaciones Maestro-Carrera y Materias-Carrera
for id_maestro, id_carrera in maestros_carrera:
    cursor.execute("INSERT INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)", (id_maestro, id_carrera))

for id_materia, id_carrera in materias_carrera:
    cursor.execute("INSERT INTO Materias_Carreras (id_materia, id_carrera) VALUES (?, ?)", (id_materia, id_carrera))

# Relación Alumnos-Materias
for id_alumno, id_materia in alumnos_materias:
    cursor.execute("INSERT INTO Alumno_Materias (id_alumno, id_materia) VALUES (?, ?)", (id_alumno, id_materia))

# Guardar cambios
conexion.commit()
print("Datos insertados correctamente.")
"""
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

    cursor.execute("SELECT * FROM Alumnos")
    print("\nAlumnos:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Alumno_Materias")
    print("\nAlumno_Materias:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Maestro_Carreras")
    print("\nMaestro_Carreras:")
    for fila in cursor.fetchall():
        print(fila)

    cursor.execute("SELECT * FROM Materias_Carreras")
    print("\nMaterias_Carreras:")
    for fila in cursor.fetchall():
        print(fila)

mostrar_datos()
# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()
