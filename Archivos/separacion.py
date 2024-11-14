import pandas as pd

# Cargar el archivo CSV
df = pd.read_csv('Archivos/actors.csv') ###aqui va donde esta el archivo

# Dividir en partes más pequeñas (por ejemplo, de 100 MB)
chunk_size = 100000  # Ajusta según el tamaño del archivo
for i in range(0, len(df), chunk_size):
    df[i:i+chunk_size].to_csv(f'actors_part{i//chunk_size + 1}.csv', index=False) ###aqui hay q cambiar como se va a llamar

