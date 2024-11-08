import tkinter as tk
import Authentication as autenticacion 
from tkinter import messagebox

def abrir_menu_principal(user_id, rol):
    menu = tk.Tk()
    menu.title("-Menú Principal-")
    menu.geometry("400x300")

    tk.Label(menu, text=f"Bienvenido, {rol}", font=("Helvetica", 16)).pack(pady=10)

    menu.mainloop()

def login(event=None): 
    # Obtener el correo y la contraseña ingresados en los campos correspondientes
    correo = username_entry.get()
    contraseña = password_entry.get()

    # Llamada a la función de autenticación para verificar las credenciales
    usuario = autenticacion.iniciar_sesion(correo, contraseña)

    # Verificar si la autenticación fue exitosa
    if usuario:
        # Si el usuario fue encontrado, extraer ID y rol
        user_id = usuario[0]  
        rol = usuario[1]      

        # Mostrar un mensaje de bienvenida al usuario
        messagebox.showinfo("Login Exitoso", f"Bienvenido, {correo}")
        
        # Cerrar la ventana de inicio de sesión después de un breve retardo
        root.after(100, root.destroy)  
        
        # Llamar a la función que abre el menú principal con el ID y rol del usuario
        abrir_menu_principal(user_id, rol)
    else:
        # Si la autenticación falla, mostrar un mensaje de error
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
