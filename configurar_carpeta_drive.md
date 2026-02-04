# Guía para Configurar la Carpeta de Drive

## Paso 1: Crear la Carpeta en tu Drive Personal

1. Ve a tu Google Drive personal: https://drive.google.com
2. Crea una nueva carpeta llamada: **"Heineken QA Compliance"** (o el nombre que prefieras)
3. Haz clic derecho en la carpeta → **"Compartir"** o haz clic en el ícono de compartir

## Paso 2: Compartir con la Cuenta de Servicio

1. En el cuadro de compartir, agrega el email de tu **cuenta de servicio** (lo encuentras en Google Cloud Console → IAM → Service accounts, o en el archivo `credentials.json` como `client_email`).
2. Dale permisos de **"Editor"** (no solo "Lector")
3. Haz clic en **"Enviar"** o **"Listo"**

## Paso 3: Obtener el ID de la Carpeta

1. Abre la carpeta que acabas de crear
2. Mira la URL en tu navegador, debería verse así:
   ```
   https://drive.google.com/drive/folders/1ABC123XYZ789...
   ```
3. El ID es la parte después de `/folders/`
   - Ejemplo: Si la URL es `https://drive.google.com/drive/folders/1ABC123XYZ789`
   - El ID es: `1ABC123XYZ789`

## Paso 4: Actualizar el ID en secrets.toml

1. Abre el archivo `.streamlit/secrets.toml`
2. Reemplaza el valor de `GOOGLE_DRIVE_FOLDER_ID` con el nuevo ID:
   ```toml
   GOOGLE_DRIVE_FOLDER_ID = "TU_NUEVO_ID_AQUI"
   ```
3. Guarda el archivo

## Paso 5: Verificar

1. Ejecuta el script de diagnóstico:
   ```bash
   python3 diagnostico_drive.py
   ```
2. Deberías ver: ✅ Carpeta accesible

## Nota Importante

- La carpeta debe estar en **TU Drive personal**, no en un Drive compartido
- La cuenta de servicio debe tener permisos de **"Editor"** (no solo "Lector")
- Si cambias el ID, reinicia la aplicación Streamlit


