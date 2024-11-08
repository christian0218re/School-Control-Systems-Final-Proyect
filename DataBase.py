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
    correo TEXT UNIQUE NOT NULL,
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
    id_usuario INTEGER NOT NULL,
    id_carrera INTEGER,
    fecha_ingreso DATE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario),
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);

-- Creación de la tabla Maestros
CREATE TABLE IF NOT EXISTS Maestros (
    id_maestro INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL,
    departamento TEXT,
    especialidad TEXT,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario)
);

-- Creación de la tabla Materias
CREATE TABLE IF NOT EXISTS Materias (
    id_materia INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_materia TEXT NOT NULL,
    codigo_materia TEXT UNIQUE NOT NULL
);

-- Creación de la tabla intermedia Materias_Carreras
CREATE TABLE IF NOT EXISTS Materias_Carreras (
    id_materia INTEGER NOT NULL,
    id_carrera INTEGER NOT NULL,
    PRIMARY KEY (id_materia, id_carrera),
    FOREIGN KEY (id_materia) REFERENCES Materias(id_materia),
    FOREIGN KEY (id_carrera) REFERENCES Carreras(id_carrera)
);
"""
# Ejecutar el script SQL
cursor.executescript(script_sql)

# Verificar y agregar un usuario administrador
cursor.execute("SELECT * FROM Usuarios WHERE correo = ?", ('admin',))
admin_existe = cursor.fetchone()

if not admin_existe:
    cursor.execute('''
        INSERT INTO Usuarios (nombre, correo, contraseña, tipo_usuario) 
        VALUES (?, ?, ?, ?)
    ''', ('admin', 'admin', 'admin', 'administrador'))
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
    else:
        print(f"La carrera '{carrera}' ya existe.")



# Verificar y agregar materias predeterminadas
materias = [
    ('Matemáticas Discretas', 'MAT101'),
    ('Derecho Penal', 'DER201'),
    ('Anatomía', 'MED301')
]
for nombre_materia, codigo_materia in materias:
    cursor.execute("SELECT * FROM Materias WHERE codigo_materia = ?", (codigo_materia,))
    materia_existe = cursor.fetchone()
    if not materia_existe:
        cursor.execute("INSERT INTO Materias (nombre_materia, codigo_materia) VALUES (?, ?)", (nombre_materia, codigo_materia))
        print(f"Materia '{nombre_materia}' creada con éxito.")
    else:
        print(f"La materia '{nombre_materia}' ya existe.")





# Confirmar los cambios y cerrar la conexión
conexion.commit()
conexion.close()
