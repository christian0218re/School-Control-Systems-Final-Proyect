import tkinter as tk
import Authentication as autenticacion
from tkinter import messagebox
from Carrera import createCareerWindow

def abrir_menu_principal(user_id, rol, nombre):
    # Cambiar de Tk() a Toplevel() para abrir una nueva ventana sin duplicar la ventana principal
    menu = tk.Toplevel()
    menu.title("-Menú Principal-")
    menu.geometry("600x400")

    barra_menus = tk.Menu(menu)

    menu_login = tk.Menu(barra_menus, tearoff=0)
    menu_login.add_command(label="Cerrar Sesión", command=menu.destroy)

    menu_admin = tk.Menu(barra_menus, tearoff=0)
    menu_admin.add_command(label="Carrera", command=createCareerWindow)

    menu_alumnos = tk.Menu(barra_menus, tearoff=0)
    menu_alumnos.add_command(label="Administrar Alumnos")

    menu_maestros = tk.Menu(barra_menus, tearoff=0)
    menu_maestros.add_command(label="Administrar Maestros")

    # Agregar cada menú a la barra de menús
    barra_menus.add_cascade(label="Login", menu=menu_login)
    if rol == "administrador":
        barra_menus.add_cascade(label="Admin", menu=menu_admin)
    
    if rol == "maestro":
        barra_menus.add_cascade(label="Algo", menu=menu_maestros)

    if rol == "alumno":
        barra_menus.add_cascade(label="Algo", menu=menu_alumnos)

    menu.config(menu=barra_menus)

    tk.Label(menu, text=f"Bienvenido, {nombre}", font=("Helvetica", 16)).pack(pady=10)

# Función de login
def login(event=None): 
    correo = username_entry.get()
    contraseña = password_entry.get()

    # Llamada a la función de autenticación para verificar las credenciales
    usuario = autenticacion.iniciar_sesion(correo, contraseña)

    # Verificar si la autenticación fue exitosa
    if usuario:
        user_id = usuario[0]  
        nombre = usuario[1]
        rol = usuario[2]    

        messagebox.showinfo("Login Exitoso", f"Bienvenido, {correo}")
        
        abrir_menu_principal(user_id, rol, nombre)  # Abrir el menú principal
        
        # Ocultar la ventana de login
        root.withdraw()  # Oculta la ventana de login, no la destruye
        
    else:
        messagebox.showerror("Error", "Correo o contraseña incorrectos")

# Ventana de login
root = tk.Tk()
root.title("Login - Farmacia CUCEI")
root.geometry("300x200")

tk.Label(root, text="Correo:").pack(pady=10)
username_entry = tk.Entry(root)
username_entry.pack(pady=5)

tk.Label(root, text="Contraseña:").pack(pady=10)
password_entry = tk.Entry(root, show="*")
password_entry.pack(pady=5)

# Botón de login y asignación de la tecla Enter
login_button = tk.Button(root, text="Login", width=10, command=login)
login_button.pack(pady=20)
root.bind('<Return>', login)  # Vincula la tecla Enter con la función login

root.mainloop()

