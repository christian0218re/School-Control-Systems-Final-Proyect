import tkinter as tk
import Authentication as autenticacion
from tkinter import messagebox
from Carrera import createCareerWindow
from Estudiantes import createStudentWindow
from Usuarios import createUserWindow
from Materias import createMateriaWindow
from horario import createHorarioWindow 
from Grupo import createGrupoWindow
from pleanacion import createPlaneacionWindow
from Salones import createClassroomWindow
from Maestros import createTeacherWindow
from GenerarGruposAuto import createGenerarGruposWindow

def abrir_menu_principal(user_id, rol, nombre):
    menu = tk.Toplevel()
    menu.title("-Menú Principal-")
    menu.geometry("600x400")

    barra_menus = tk.Menu(menu)

    menu_login = tk.Menu(barra_menus, tearoff=0)
    menu_login.add_command(label="Cerrar Sesión", command=menu.destroy)

    menu_admin = tk.Menu(barra_menus, tearoff=0)
    menu_admin.add_command(label="Carrera", command=createCareerWindow)
    menu_admin.add_command(label="Estudiantes", command=lambda: createStudentWindow(user_id,rol))
    menu_admin.add_command(label="Materias", command=createMateriaWindow)
    menu_admin.add_command(label="Horarios", command=createHorarioWindow)
    menu_admin.add_command(label="Usuarios", command=createUserWindow)
    menu_admin.add_command(label="Grupo", command=createGrupoWindow)
    menu_admin.add_command(label="Salones", command=createClassroomWindow)
    menu_admin.add_command(label="Maestros", command=createTeacherWindow)
    menu_admin.add_command(label="Generar Grupos", command=createGenerarGruposWindow)

    menu_alumnos = tk.Menu(barra_menus, tearoff=0)
    menu_alumnos.add_command(label="Perfil", command=lambda: createStudentWindow(user_id,rol))

    menu_maestros = tk.Menu(barra_menus, tearoff=0)
    menu_maestros.add_command(label="Administrar Maestros")

    menu_planeacion = tk.Menu(barra_menus, tearoff=0)
    menu_planeacion.add_command(label="Abrir Planeación", command=createPlaneacionWindow)

    barra_menus.add_cascade(label="Login", menu=menu_login)
    if rol == "administrador":
        barra_menus.add_cascade(label="Admin", menu=menu_admin)
    
    if rol == "maestro":
        barra_menus.add_cascade(label="Algo", menu=menu_maestros)

    if rol == "alumno":
        barra_menus.add_cascade(label="Alumno", menu=menu_alumnos)

        
    barra_menus.add_cascade(label="Planeación", menu=menu_planeacion)

    menu.config(menu=barra_menus)

    tk.Label(menu, text=f"Bienvenido, {nombre}", font=("Helvetica", 16)).pack(pady=10)

def login(event=None): 
    correo = username_entry.get()
    contraseña = password_entry.get()

    usuario = autenticacion.iniciar_sesion(correo, contraseña)

    if usuario:
        user_id = usuario[0]  
        nombre = usuario[1]
        rol = usuario[2]    

        messagebox.showinfo("Login Exitoso", f"Bienvenido, {correo}")
        
        abrir_menu_principal(user_id, rol, nombre)  
        
        
        root.withdraw()  
        
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos")


root = tk.Tk()
root.title("Login - Farmacia CUCEI")
root.geometry("300x200")

tk.Label(root, text="Correo:").pack(pady=10)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

tk.Label(root, text="Contraseña:").pack(pady=10)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

login_button = tk.Button(root, text="Login", width=10, command=login)
login_button.pack(pady=20)
root.bind('<Return>', login)  

root.mainloop()

