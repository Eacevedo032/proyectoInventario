import os
import datetime
import subprocess

# CONFIGURACION DATOS DEL GUARDADO
usuario = "root"
contrasena = "unp.1234"
base_datos = "inventario_db"
ruta_guardado = "C:/backups_inventario_db"

# Crear carpeta si no existe
os.makedirs(ruta_guardado, exist_ok=True)

# Nombre del archivo con fecha y hora
fecha = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
nombre_archivo = f"backup_{base_datos}_{fecha}.sql"
ruta_completa = os.path.join(ruta_guardado, nombre_archivo)

# Comando para ejecutar mysqldump
comando = f"mysqldump -u {usuario} -p{contrasena} {base_datos} > \"{ruta_completa}\""

# Ejecutar comando en terminal
resultado = subprocess.run(comando, shell=True)

# Verificación
if resultado.returncode == 0:
    print(f"Backup exitoso: {ruta_completa}")
else:
    print("Error al realizar el backup.")

#Restaurar datos manualmente desde el CMD como "ejecutar como administrador
#  mysql -u root -p inventario_db < "C:\backups_inventario_db\backup_inventario_db_2025-05-21_12-04-47.sql o nombre del backup"
# 
# Script para buackup manual de la BD
# python scripts/backup_mysql.py
# "