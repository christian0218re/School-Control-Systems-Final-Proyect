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

CREATE TABLE IF NOT EXISTS Maestros (
    id_maestro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    nombre TEXT NOT NULL,
    a_paterno TEXT NOT NULL,
    a_materno TEXT NOT NULL,
    correo TEXT NOT NULL,
    grado_estudio TEXT CHECK(grado_estudio IN ('Licenciatura', 'Maestria', 'Doctorado')) NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
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

-- Creación de la tabla intermedia Materias_Carreras
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

# Verificar y agregar un usuario administrador
cursor.execute("SELECT * FROM Usuarios WHERE correo = ?", ('admin',))
admin_existe = cursor.fetchone()

if not admin_existe:
    cursor.execute('''
        INSERT INTO Usuarios (nombre,a_paterno, a_materno, correo, contraseña,nombre_usuario, tipo_usuario)
        VALUES (?, ?, ?, ?, ?, ?, ?)'''
    , ('admin', 'admin' , 'admin', 'admin','admin','admin','administrador'))
    print("Usuario admin creado con éxito.")
else:
    print("El usuario admin ya existe.")


# Verificar y agregar carreras predeterminadas
carreras = ['Ingeniería en Computación', 'Derecho', 'Medicina']
for carrera in carreras:
    cursor.execute("SELECT * FROM Carreras WHERE nombre_carrera = ?", (carrera,))
    carrera_existe = cursor.fetchone()
    if not carrera_existe:
        cursor.execute("INSERT INTO Carreras (nombre_carrera) VALUES (?)", (carrera,))
        print(f"Carrera '{carrera}' creada con éxito.")

# Verificar y agregar materias predeterminadas
materias = [
    ('Matemáticas Discretas', 'MAT101', 8, 'septimo'),
    ('Derecho Penal', 'DER201', 5, 'noveno'),
    ('Anatomía', 'MED301', 4, 'tercero')
]
for nombre_materia, codigo_materia, creditos, semestre in materias:
    cursor.execute("SELECT * FROM Materias WHERE codigo_materia = ?", (codigo_materia,))
    materia_existe = cursor.fetchone()
    if not materia_existe:
        cursor.execute("INSERT INTO Materias (nombre_materia, codigo_materia, creditos, semestre) VALUES (?, ?, ?, ?)",
                       (nombre_materia, codigo_materia, creditos, semestre))
        print(f"Materia '{nombre_materia}' creada con éxito.")




# Agregar usuarios y maestros predeterminados
usuarios_maestros = [
    ("Juan", "Pérez", "López", "juan.perez@ejemplo.com", "juan123", "1234", "maestro", "Doctorado"),
    ("María", "García", "Martínez", "maria.garcia@ejemplo.com", "maria123", "5678", "maestro", "Maestria")
]

for nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario, grado_estudio in usuarios_maestros:
    # Verificar si el usuario ya existe
    cursor.execute("SELECT * FROM Usuarios WHERE correo = ?", (correo,))
    usuario_existe = cursor.fetchone()
    
    if not usuario_existe:
        # Crear usuario
        cursor.execute("""
            INSERT INTO Usuarios (nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nombre, a_paterno, a_materno, correo, nombre_usuario, contraseña, tipo_usuario))
        print(f"Usuario '{nombre_usuario}' creado con éxito.")
    
    # Obtener id_usuario del usuario creado o existente
    cursor.execute("SELECT id_usuario FROM Usuarios WHERE correo = ?", (correo,))
    id_usuario = cursor.fetchone()[0]
    
    # Verificar si el maestro ya existe
    cursor.execute("SELECT * FROM Maestros WHERE id_usuario = ?", (id_usuario,))
    maestro_existe = cursor.fetchone()

    if not maestro_existe:
        # Crear maestro
        cursor.execute("""
            INSERT INTO Maestros (id_usuario, nombre, a_paterno, a_materno, correo, grado_estudio)
            VALUES (?, ?, ?, ?, ?, ?) """, (id_usuario, nombre, a_paterno, a_materno, correo, grado_estudio))
        print(f"Maestro '{nombre} {a_paterno}' creado con éxito.")


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
        

"""
# Continuar con la asignación de carreras y materias como antes
cursor.execute("SELECT id_maestro, nombre FROM Maestros")
maestros_ids = cursor.fetchall()

for id_maestro, nombre in maestros_ids:
    if nombre == "Juan":
        # Juan tendrá todas las carreras y materias
        cursor.execute("SELECT id_carrera FROM Carreras")
        carreras = cursor.fetchall()
        cursor.execute("SELECT id_materia FROM Materias")
        materias = cursor.fetchall()

        for (id_carrera,) in carreras:
            cursor.execute("INSERT OR IGNORE INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)", (id_maestro, id_carrera))
        for (id_materia,) in materias:
            cursor.execute("INSERT OR IGNORE INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)", (id_maestro, id_materia))

    elif nombre == "María":
        # María tendrá todas las carreras pero una sola materia (Matemáticas Discretas)
        cursor.execute("SELECT id_carrera FROM Carreras")
        carreras = cursor.fetchall()
        cursor.execute("SELECT id_materia FROM Materias WHERE nombre_materia = 'Matemáticas Discretas'")
        materia = cursor.fetchone()

        if materia:
            id_materia = materia[0]
            for (id_carrera,) in carreras:
                cursor.execute("INSERT OR IGNORE INTO Maestro_Carreras (id_maestro, id_carrera) VALUES (?, ?)", (id_maestro, id_carrera))
                cursor.execute("INSERT OR IGNORE INTO Maestro_Materias (id_maestro, id_materia) VALUES (?, ?)", (id_maestro, id_materia))

print("Usuarios, maestros y asignaciones creados con éxito.")
"""

# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()
