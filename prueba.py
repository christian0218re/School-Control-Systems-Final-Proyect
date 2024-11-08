# Productos.py
from baseDatos import conectar
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import messagebox

def createProductWindow():
    # Función para crear un nuevo producto
    def crear_producto():
        conn = conectar()
        cursor = conn.cursor()

        # Obtener los valores de los campos de entrada
        productoId = idEntry.get()
        nombre = nameEntry.get()
        descripcion = descriptionEntry.get()
        precio = precioEntry.get()
        stock = stockEntry.get()

        proveedor_nombre = proveedorCombo.get()
        proveedorId = proveedores_dict.get(proveedor_nombre)

        # Validaciones
        try:
            precio = float(precio)  # Asegurarse de que el precio es un número decimal
            stock = int(stock)  # Asegurarse de que el stock es un número entero
        except ValueError:
            messagebox.showinfo("Error", "El precio debe ser un número decimal y el stock un número entero")
            return

        if precio <= 0:
            messagebox.showinfo("Error", "El precio debe ser mayor a cero")
            return

        if stock < 0:
            messagebox.showinfo("Error", "El stock no puede ser negativo")
            return

        try:
            # Verificar que el productoId no esté en uso
            cursor.execute("SELECT * FROM productos WHERE productoId = ?", (productoId,))
            if cursor.fetchone():
                messagebox.showinfo("Error", "El ID del producto ya está registrado")
                return

            if nombre and descripcion:  # Validar que nombre y descripción estén llenos
                cursor.execute("""
                    INSERT INTO productos (productoId, nombre, descripcion, precio, stock, proveedorId)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (productoId, nombre, descripcion, precio, stock, proveedorId))
                conn.commit()
                messagebox.showinfo("Éxito", "El producto ha sido creado correctamente")
                cleanProductWindow()
            else:
                messagebox.showinfo("Error", "Por favor rellene los campos Nombre y Descripción antes de continuar")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Función para obtener la lista de proveedores
    def obtener_proveedores():
        conn = conectar()
        cursor = conn.cursor()

        # Obtener la lista de proveedores (nombre y proveedorId)
        cursor.execute("SELECT proveedorId, nombre FROM proveedores")
        proveedores = cursor.fetchall()
        conn.close()

        # Crear un diccionario de proveedorId y nombre
        return {proveedor[1]: proveedor[0] for proveedor in proveedores}

    # Función para buscar un producto
    def buscar_producto():
        conn = conectar()
        cursor = conn.cursor()
        buscarProducto = idSearch.get()

        try:
            cursor.execute("SELECT * FROM productos WHERE productoId = ?", (buscarProducto,))
            producto = cursor.fetchone()

            if producto:
                # Llenar los campos del formulario con los datos del producto
                idEntry.delete(0, tk.END)
                idEntry.insert(0, producto[0])
                nameEntry.delete(0, tk.END)
                nameEntry.insert(0, producto[1])
                descriptionEntry.delete(0, tk.END)
                descriptionEntry.insert(0, producto[2])
                precioEntry.delete(0, tk.END)
                precioEntry.insert(0, producto[3])
                stockEntry.delete(0, tk.END)
                stockEntry.insert(0, producto[4])

                # Convertir proveedorId en nombre de proveedor para el combobox
                proveedorId = producto[5]
                for nombre, id in proveedores_dict.items():
                    if id == proveedorId:
                        proveedorCombo.set(nombre)
                        break
            else:
                messagebox.showinfo("Error", "Producto no encontrado")
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    # Función para actualizar un producto
    def actualizar_producto():
        conn = conectar()
        cursor = conn.cursor()
        productoId = idEntry.get()
        nombre = nameEntry.get()
        descripcion = descriptionEntry.get()
        precio = precioEntry.get()
        stock = stockEntry.get()

        # Obtener el proveedor seleccionado del combobox
        proveedor_nombre = proveedorCombo.get()
        proveedorId = proveedores_dict.get(proveedor_nombre)

        try:
            precio = float(precio)
            stock = int(stock)
        except ValueError:
            messagebox.showinfo("Error", "El precio debe ser un número decimal y el stock un número entero")
            return

        if not productoId or not nombre or not descripcion or not precio or not stock or not proveedorId:
            messagebox.showinfo("Error", "Por favor rellene todos los campos antes de continuar")
            return

        # Verificar que el producto exista
        cursor.execute("SELECT * FROM productos WHERE productoId = ?", (productoId,))
        if not cursor.fetchone():
            messagebox.showinfo("Error", "El producto no existe")
            return

        try:
            cursor.execute("""
                UPDATE productos
                SET nombre = ?, descripcion = ?, precio = ?, stock = ?, proveedorId = ?
                WHERE productoId = ?
            """, (nombre, descripcion, precio, stock, proveedorId, productoId))
            conn.commit()

            messagebox.showinfo("Éxito", "Producto actualizado correctamente")
            cleanProductWindow()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def eliminar_producto():
        conn = conectar()
        cursor = conn.cursor()
        productoId = idEntry.get()

        try:
            cursor.execute("DELETE FROM productos WHERE productoId = ?", (productoId,))
            conn.commit()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            cleanProductWindow()
        except Exception as e:
            messagebox.showinfo("Error", str(e))
        finally:
            conn.close()

    def getCurrentID():
        conn = conectar()
        cursor = conn.cursor()

        # Obtener el último ID de la base de datos de productos
        cursor.execute("SELECT MAX(productoId) FROM productos")
        last_id = cursor.fetchone()[0]

        # Si no hay productos, el ID inicial será 1, de lo contrario será el siguiente al último ID
        next_id = 1 if last_id is None else last_id + 1

        cleanProductWindow()
        idEntry.insert(0, next_id)

        conn.close()

    # Función para limpiar los campos
    def cleanProductWindow():
        idEntry.delete(0, tk.END)
        nameEntry.delete(0, tk.END)
        descriptionEntry.delete(0, tk.END)
        precioEntry.delete(0, tk.END)
        stockEntry.delete(0, tk.END)
        proveedorCombo.set('')  # Limpiar el combobox de proveedores

    # Crear la ventana principal para gestionar productos
    product_window = tk.Tk()
    product_window.title("Productos")
    product_window.geometry("650x590")

    # Etiquetas y entradas para buscar productos por ID
    tk.Label(product_window, text='Ingrese el ID').grid(row=0, column=0, padx=10, pady=10)
    idSearch = tk.Entry(product_window)
    idSearch.grid(row=0, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Buscar', command=buscar_producto).grid(row=0, column=2, padx=10, pady=10)

    # Etiquetas para los campos del producto
    tk.Label(product_window, text='ID Producto').grid(row=1, column=0, padx=10, pady=10)
    tk.Label(product_window, text='Nombre del Producto').grid(row=2, column=0, padx=10, pady=10)
    tk.Label(product_window, text='Descripción').grid(row=3, column=0, padx=10, pady=10)
    tk.Label(product_window, text='Precio').grid(row=4, column=0, padx=10, pady=10)
    tk.Label(product_window, text='Stock').grid(row=5, column=0, padx=10, pady=10)
    tk.Label(product_window, text='Proveedor').grid(row=6, column=0, padx=10, pady=10)

    # Entradas para los campos del producto
    idEntry = tk.Entry(product_window)
    idEntry.grid(row=1, column=1, padx=10, pady=10)
    nameEntry = tk.Entry(product_window)
    nameEntry.grid(row=2, column=1, padx=10, pady=10)
    descriptionEntry = tk.Entry(product_window)
    descriptionEntry.grid(row=3, column=1, padx=10, pady=10)
    precioEntry = tk.Entry(product_window)
    precioEntry.grid(row=4, column=1, padx=10, pady=10)
    stockEntry = tk.Entry(product_window)
    stockEntry.grid(row=5, column=1, padx=10, pady=10)

    # Menú desplegable para seleccionar proveedor
    proveedores_dict = obtener_proveedores()  # Obtener diccionario de proveedores
    proveedorCombo = ttk.Combobox(product_window, values=list(proveedores_dict.keys()))
    proveedorCombo.grid(row=6, column=1, padx=10, pady=10)

    # Botones para las acciones de los productos
    tk.Button(product_window, text='Nuevo', width=20, command=getCurrentID).grid(row=7, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Actualizar', width=20, command=actualizar_producto).grid(row=8, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Guardar', width=20, command=crear_producto).grid(row=9, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Eliminar', width=20, command=eliminar_producto).grid(row=10, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Cancelar', width=20, command=cleanProductWindow).grid(row=11, column=1, padx=10, pady=10)
    tk.Button(product_window, text='Salir', width=20, command=product_window.destroy).grid(row=0, column=3, padx=10, pady=10)

    product_window.mainloop()