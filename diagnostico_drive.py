#!/usr/bin/env python3
"""
Script de diagnóstico para Google Drive API
Verifica todos los aspectos de la configuración necesarios para guardar archivos
"""

import os
import json
from datetime import datetime

print("=" * 60)
print("DIAGNÓSTICO DE GOOGLE DRIVE API")
print("=" * 60)
print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. Verificar librerías
print("1. VERIFICANDO LIBRERÍAS...")
print("-" * 60)
try:
    import gspread
    print("✅ gspread instalado")
except ImportError:
    print("❌ gspread NO está instalado")
    print("   Ejecuta: pip install gspread")

try:
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    print("✅ google-api-python-client instalado")
except ImportError:
    print("❌ google-api-python-client NO está instalado")
    print("   Ejecuta: pip install google-api-python-client")

try:
    from google.oauth2 import service_account
    print("✅ google-auth instalado")
except ImportError:
    print("❌ google-auth NO está instalado")
    print("   Ejecuta: pip install google-auth")

try:
    from oauth2client.service_account import ServiceAccountCredentials
    print("✅ oauth2client instalado")
except ImportError:
    print("⚠️  oauth2client NO está instalado (puede no ser necesario)")

print()

# 2. Verificar archivo de credenciales
print("2. VERIFICANDO ARCHIVO DE CREDENCIALES...")
print("-" * 60)
credentials_path = "credentials.json"
if os.path.exists(credentials_path):
    print(f"✅ Archivo encontrado: {credentials_path}")
    try:
        with open(credentials_path, 'r') as f:
            creds_data = json.load(f)
        
        # Verificar campos necesarios
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_data]
        
        if missing_fields:
            print(f"❌ Faltan campos en credentials.json: {', '.join(missing_fields)}")
        else:
            print("✅ Estructura del archivo de credenciales es válida")
            print(f"   - Tipo: {creds_data.get('type', 'N/A')}")
            print(f"   - Project ID: {creds_data.get('project_id', 'N/A')}")
            print(f"   - Client Email: {creds_data.get('client_email', 'N/A')}")
            
            # Mostrar email de la cuenta de servicio
            service_email = creds_data.get('client_email', '')
            if service_email:
                print(f"\n   📧 EMAIL DE LA CUENTA DE SERVICIO: {service_email}")
                print(f"   ⚠️  IMPORTANTE: Comparte la carpeta de Drive con este email")
    except json.JSONDecodeError:
        print("❌ El archivo credentials.json no es un JSON válido")
    except Exception as e:
        print(f"❌ Error al leer credentials.json: {e}")
else:
    print(f"❌ Archivo NO encontrado: {credentials_path}")
    print("   Necesitas descargar el archivo JSON de Google Cloud Console")

print()

# 3. Verificar secrets.toml
print("3. VERIFICANDO CONFIGURACIÓN (secrets.toml)...")
print("-" * 60)
secrets_path = ".streamlit/secrets.toml"
if os.path.exists(secrets_path):
    print(f"✅ Archivo encontrado: {secrets_path}")
    try:
        import tomli
        with open(secrets_path, 'rb') as f:
            secrets = tomli.load(f)
        
        if 'GOOGLE_DRIVE_FOLDER_ID' in secrets:
            folder_id = secrets['GOOGLE_DRIVE_FOLDER_ID']
            print(f"✅ GOOGLE_DRIVE_FOLDER_ID configurado: {folder_id}")
        else:
            print("❌ GOOGLE_DRIVE_FOLDER_ID NO está configurado")
        
        if 'GOOGLE_SHEET_ID' in secrets:
            print(f"✅ GOOGLE_SHEET_ID configurado: {secrets['GOOGLE_SHEET_ID']}")
        else:
            print("⚠️  GOOGLE_SHEET_ID NO está configurado")
            
    except ImportError:
        print("⚠️  No se puede leer TOML (instala: pip install tomli)")
        # Intentar lectura manual
        with open(secrets_path, 'r') as f:
            content = f.read()
            if 'GOOGLE_DRIVE_FOLDER_ID' in content:
                print("✅ GOOGLE_DRIVE_FOLDER_ID encontrado en el archivo")
            else:
                print("❌ GOOGLE_DRIVE_FOLDER_ID NO encontrado")
    except Exception as e:
        print(f"⚠️  Error al leer secrets.toml: {e}")
else:
    print(f"⚠️  Archivo NO encontrado: {secrets_path}")

print()

# 4. Intentar conectar con Drive
print("4. PROBANDO CONEXIÓN CON GOOGLE DRIVE...")
print("-" * 60)
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    
    SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    
    if os.path.exists(credentials_path):
        try:
            creds = service_account.Credentials.from_service_account_file(
                credentials_path, 
                scopes=SCOPE
            )
            print("✅ Credenciales cargadas correctamente")
            
            service = build('drive', 'v3', credentials=creds)
            print("✅ Servicio de Drive creado")
            
            # Intentar obtener información del usuario
            try:
                about = service.about().get(fields='user,storageQuota').execute()
                user_email = about.get('user', {}).get('emailAddress', 'N/A')
                print(f"✅ API de Drive habilitada y funcionando")
                print(f"   Usuario: {user_email}")
            except Exception as e:
                error_str = str(e)
                if "403" in error_str or "accessNotConfigured" in error_str:
                    print("❌ ERROR: La API de Google Drive NO está habilitada")
                    print("\n   SOLUCIÓN:")
                    print("   1. Ve a: https://console.cloud.google.com/apis/library/drive.googleapis.com")
                    print("   2. Selecciona tu proyecto")
                    print("   3. Haz clic en 'HABILITAR'")
                    print("   4. Espera 1-2 minutos y vuelve a intentar")
                elif "401" in error_str:
                    print("❌ ERROR: Problema de autenticación")
                    print("   Verifica que el archivo credentials.json sea válido")
                else:
                    print(f"❌ ERROR al verificar API: {error_str}")
            
            # Intentar acceder a la carpeta raíz
            try:
                # Leer folder_id desde secrets
                folder_id = None
                if os.path.exists(secrets_path):
                    try:
                        import tomli
                        with open(secrets_path, 'rb') as f:
                            secrets = tomli.load(f)
                            folder_id = secrets.get('GOOGLE_DRIVE_FOLDER_ID')
                    except:
                        # Fallback: leer manualmente
                        with open(secrets_path, 'r') as f:
                            for line in f:
                                if 'GOOGLE_DRIVE_FOLDER_ID' in line:
                                    folder_id = line.split('=')[1].strip().strip('"').strip("'")
                                    break
                
                if folder_id:
                    # Detectar si es Shared Drive (IDs empiezan con 0A)
                    is_shared_drive = folder_id.startswith('0A') and len(folder_id) > 10
                    
                    if is_shared_drive:
                        print(f"\n   Verificando acceso a Shared Drive: {folder_id}")
                        try:
                            drive = service.drives().get(
                                driveId=folder_id,
                                fields='id,name'
                            ).execute()
                            print(f"✅ Shared Drive accesible: {drive.get('name', 'N/A')}")
                            print(f"   ID: {drive.get('id', 'N/A')}")
                            print(f"\n   ✅ La cuenta de servicio es miembro del Shared Drive")
                        except Exception as e:
                            error_str = str(e)
                            if "404" in error_str:
                                print(f"❌ ERROR: El Shared Drive con ID '{folder_id}' no existe")
                                print(f"   O la cuenta de servicio no es miembro del Shared Drive")
                            elif "403" in error_str:
                                print(f"❌ ERROR: No tienes permisos para acceder al Shared Drive")
                                service_email = creds_data.get('client_email', '') if 'creds_data' in locals() else ''
                                print(f"\n   SOLUCIÓN:")
                                print(f"   1. Abre el Shared Drive en Google Drive")
                                print(f"   2. Haz clic en 'Gestionar miembros' o 'Manage members'")
                                print(f"   3. Agrega este email como miembro: {service_email}")
                                print(f"   4. Dale permisos de 'Editor' o 'Content Manager'")
                            else:
                                print(f"❌ ERROR al acceder al Shared Drive: {error_str}")
                    else:
                        print(f"\n   Verificando acceso a carpeta: {folder_id}")
                        folder = service.files().get(
                            fileId=folder_id, 
                            fields='id,name,permissions,mimeType',
                            supportsAllDrives=True
                        ).execute()
                        print(f"✅ Carpeta accesible: {folder.get('name', 'N/A')}")
                        print(f"   Tipo: {folder.get('mimeType', 'N/A')}")
                        
                        # Verificar permisos
                        permissions = folder.get('permissions', [])
                        service_email = creds_data.get('client_email', '') if 'creds_data' in locals() else ''
                        has_access = any(
                            p.get('emailAddress', '') == service_email 
                            for p in permissions
                        )
                        
                        if has_access:
                            print(f"✅ La cuenta de servicio tiene acceso a la carpeta")
                        else:
                            print(f"⚠️  ADVERTENCIA: La cuenta de servicio puede no tener acceso")
                            print(f"   Comparte la carpeta con: {service_email}")
                else:
                    print("⚠️  No se pudo leer GOOGLE_DRIVE_FOLDER_ID de secrets.toml")
                    
            except Exception as e:
                error_str = str(e)
                if "404" in error_str:
                    print(f"❌ ERROR: La carpeta con ID '{folder_id}' no existe")
                    print("   Verifica que el ID en secrets.toml sea correcto")
                elif "403" in error_str:
                    print(f"❌ ERROR: No tienes permisos para acceder a la carpeta '{folder_id}'")
                    print(f"\n   SOLUCIÓN:")
                    print(f"   1. Abre la carpeta en Google Drive")
                    print(f"   2. Haz clic en 'Compartir'")
                    print(f"   3. Agrega el email: {service_email}")
                    print(f"   4. Dale permisos de 'Editor'")
                else:
                    print(f"❌ ERROR al acceder a la carpeta: {error_str}")
            
        except Exception as e:
            print(f"❌ Error al crear servicio: {e}")
    else:
        print("❌ No se puede probar la conexión: credentials.json no existe")
        
except Exception as e:
    print(f"❌ Error general: {e}")

print()
print("=" * 60)
print("RESUMEN DEL DIAGNÓSTICO")
print("=" * 60)
print("\nSi hay errores, sigue estos pasos:")
print("1. Verifica que todas las librerías estén instaladas")
print("2. Asegúrate de que credentials.json sea válido")
print("3. Habilita la API de Drive en Google Cloud Console")
print("4. Comparte la carpeta de Drive con el email de la cuenta de servicio")
print("5. Verifica que GOOGLE_DRIVE_FOLDER_ID esté correcto en secrets.toml")
print()


