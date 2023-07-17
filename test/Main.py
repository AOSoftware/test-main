import sqlite3
from tkinter import Tk, Button, Label, Frame, LEFT, Toplevel, Entry

data_frame = None  # Variable global para el frame de datos

def edit_zone(zone_id, zone_name):
    # Lógica de edición de la zona seleccionada
    print("Editando zona:", zone_name)
    # Abrir la pantalla emergente
    open_popup(zone_id, zone_name)

def open_popup(zone_id, zone_name):
    # Crear la ventana emergente
    popup = Toplevel(root)
    popup.title("Distributions")

    # Etiqueta de mensaje
    message_label = Label(popup, text="Zona: " + zone_name)
    message_label.pack(pady=10)

    # Frame para los botones
    buttons_frame = Frame(popup)
    buttons_frame.pack(pady=5)

    # Ancho de los botones
    button_width = 15

    # Botón Modificar
    modify_button = Button(buttons_frame, text="Modificar", font=("Arial", 12), bg="blue", fg="white", width=button_width,
                           command=lambda: open_edit_popup(zone_id, zone_name, popup))
    modify_button.pack(side=LEFT, padx=5)

    # Botón Crear
    create_button = Button(buttons_frame, text="Agregar", font=("Arial", 12), bg="green", fg="white", width=button_width)
    create_button.pack(side=LEFT, padx=5)

    # Botón Eliminar
    delete_button = Button(buttons_frame, text="Eliminar", font=("Arial", 12), bg="red", fg="white", width=button_width)
    delete_button.pack(side=LEFT, padx=5)

    # Botón Cancelar
    cancel_button = Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg="black", fg="white", width=button_width,
                           command=popup.destroy)
    cancel_button.pack(side=LEFT, padx=5)

def open_edit_popup(zone_id, zone_name, parent_popup):
    # Cerrar la ventana emergente padre
    parent_popup.destroy()

    # Crear la ventana emergente de edición
    edit_popup = Toplevel(root)
    edit_popup.title("Edit Distribution")

    # Etiqueta de mensaje
    message_label = Label(edit_popup, text="Zona: " + zone_name)
    message_label.pack(pady=10)

    # Obtener los porcentajes actuales de la zona
    current_percentages = get_percentages(zone_id)
    # Lista para almacenar las entradas de porcentajes
    percentage_entries = []

    for i, percentage in enumerate(current_percentages):
        # Etiqueta de porcentaje
        percentage_label = Label(edit_popup, text="Porcentaje " + str(i+1) + ":")
        percentage_label.pack()

        # Entrada de porcentaje
        entry = Entry(edit_popup)
        entry.insert(0, str(percentage))
        entry.pack()

        # Agregar la entrada a la lista
        percentage_entries.append(entry)

    # Frame para los botones
    buttons_frame = Frame(edit_popup)
    buttons_frame.pack(pady=5)

    # Ancho de los botones
    button_width = 15

    # Botón Guardar
    save_button = Button(buttons_frame, text="Guardar", font=("Arial", 12), bg="green", fg="white", width=button_width,
                         command=lambda: save_percentages(zone_id, percentage_entries, edit_popup))
    save_button.pack(side=LEFT, padx=5)

    # Botón Cancelar
    cancel_button = Button(buttons_frame, text="Cancelar", font=("Arial", 12), bg="black", fg="white", width=button_width,
                           command=edit_popup.destroy)
    cancel_button.pack(side=LEFT, padx=5)

def get_percentages(zone_id):
    # Conexión a la base de datos
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Consulta SQL para obtener los porcentajes de la zona
    query = "SELECT percentage FROM zones_distribution WHERE zone_id = ?"
    cursor.execute(query, (zone_id,))
    result = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    conn.close()

    return [row[0] for row in result]

def save_percentages(zone_id, entries, popup):
    # Obtener los porcentajes ingresados
    new_percentages = [entry.get() for entry in entries]

    # Validar que los porcentajes sean números enteros
    if not all(percentage.isdigit() for percentage in new_percentages):
        print("Error: Los porcentajes deben ser números enteros.")
        return

    # Actualizar los porcentajes en la base de datos
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Eliminar los porcentajes existentes
    delete_query = "DELETE FROM zones_distribution WHERE zone_id = ?"
    cursor.execute(delete_query, (zone_id,))

    # Insertar los nuevos porcentajes
    insert_query = "INSERT INTO zones_distribution (zone_id, percentage) VALUES (?, ?)"
    for percentage in new_percentages:
        cursor.execute(insert_query, (zone_id, percentage))

    # Confirmar los cambios en la base de datos
    conn.commit()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Cerrar la ventana emergente de edición
    popup.destroy()

    # Actualizar la ventana principal
    refresh_main_window()

def refresh_main_window():
    global data_frame  # Utilizar la variable global data_frame

    # Limpiar el frame de datos
    data_frame.destroy()

    # Crear un nuevo frame de datos
    data_frame = Frame(root)
    data_frame.pack()

    # Consultar los datos actualizados de la base de datos
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()

    # Consulta SQL para recuperar la información de las tablas
    query = """
    SELECT zones_zone.id, zones_zone.name, GROUP_CONCAT(zones_distribution.percentage || '%', ', ')
    FROM zones_zone
    INNER JOIN zones_distribution ON zones_zone.id = zones_distribution.zone_id
    GROUP BY zones_zone.id, zones_zone.name
    """

    # Ejecutar la consulta
    cursor.execute(query)
    result = cursor.fetchall()

    # Cerrar la conexión a la base de datos
    conn.close()

    # Crear un conjunto para realizar el seguimiento de las zonas mostradas
    zonas_mostradas = set()

    for row_data in result:
        zone_id, zone_name, distribution_percentages = row_data

        if zone_name not in zonas_mostradas:
            # Obtener la lista de porcentajes
            percentages = distribution_percentages.split(", ")

            # Verificar si hay 5 o más porcentajes
            if len(percentages) >= 5:
                zone_bg = "red"  # Color de fondo para zonas con 5 o más porcentajes
            else:
                zone_bg = "white"  # Color de fondo para zonas con menos de 5 porcentajes

            # Zona y Porcentajes
            zone_frame = Frame(data_frame, bg=zone_bg)
            zone_frame.pack(anchor="w")

            zone_label = Label(zone_frame, text="Zone Name: " + zone_name, font=("Arial", 12), anchor="w")
            zone_label.pack(side=LEFT)

            distribution_label = Label(zone_frame, text="Distribution: " + distribution_percentages, font=("Arial", 12), anchor="w")
            distribution_label.pack(side=LEFT)

            spacer_label = Label(zone_frame, text=" " * 100, font=("Arial", 12))
            spacer_label.pack(side=LEFT)

            # Botón "Edit"
            edit_button = Button(zone_frame, text="Edit", font=("Arial", 12), bg="blue", fg="white",
                                 command=lambda zone_id=zone_id, zone_name=zone_name: edit_zone(zone_id, zone_name))
            edit_button.pack(side=LEFT)

            # Agregar la zona mostrada al conjunto
            zonas_mostradas.add(zone_name)

# Conexión a la base de datos
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Consulta SQL para recuperar la información de las tablas
query = """
SELECT zones_zone.id, zones_zone.name, GROUP_CONCAT(zones_distribution.percentage || '%', ', ')
FROM zones_zone
INNER JOIN zones_distribution ON zones_zone.id = zones_distribution.zone_id
GROUP BY zones_zone.id, zones_zone.name
"""

# Ejecutar la consulta
cursor.execute(query)
result = cursor.fetchall()

# Cerrar la conexión a la base de datos
conn.close()

# Crear ventana principal
root = Tk()
root.title("Zones and Distributions")

# Cuadrícula para mostrar los datos
data_frame = Frame(root)
data_frame.pack()

# Actualizar la ventana principal
refresh_main_window()

# Mostrar la ventana principal
root.mainloop()
