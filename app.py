
import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import time
from datetime import datetime
import os
import io

# File Processing
from pypdf import PdfReader
from docx import Document

# Google Services
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from google.oauth2 import service_account
    GOOGLE_SERVICES_AVAILABLE = True
except ImportError:
    GOOGLE_SERVICES_AVAILABLE = False

# --- CONFIGURACIÓN E INICIALIZACIÓN ---
st.set_page_config(page_title="Heineken QA Compliance", page_icon="🍺", layout="wide")

# --- HEINEKEN THEME CSS ---
st.markdown("""
<style>
    /* VARIABLES - Colores oficiales Heineken */
    :root {
        --heineken-green: #003D2D;
        --heineken-green-light: #005A47;
        --heineken-green-hover: #00251A;
        --heineken-red: #E31E24;
        --heineken-red-light: #FF2A2A;
        --heineken-silver: #C3C3C3;
        --heineken-black: #1A1A1A;
        --heineken-white: #FFFFFF;
        --bg-color: #F5F5F5;
        --card-shadow: 0 8px 24px rgba(0, 61, 45, 0.12);
    }

    /* GENERAL */
    .stApp {
        background: linear-gradient(135deg, #F5F5F5 0%, #FFFFFF 100%);
        font-family: 'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }
    
    /* HEADER */
    header[data-testid="stHeader"] {
        background: var(--heineken-green);
        box-shadow: 0 2px 8px rgba(0, 61, 45, 0.2);
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--heineken-green) 0%, var(--heineken-green-light) 100%);
        box-shadow: 2px 0 12px rgba(0, 61, 45, 0.15);
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] div {
        color: white !important;
    }
    
    /* BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, var(--heineken-green) 0%, var(--heineken-green-light) 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 14px;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
        box-shadow: 0 4px 12px rgba(0, 61, 45, 0.25);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, var(--heineken-green-hover) 0%, var(--heineken-green) 100%);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 61, 45, 0.35);
    }
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* HEADERS */
    h1 {
        color: var(--heineken-green);
        font-weight: 700;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
        margin-bottom: 1rem;
    }
    h2 {
        color: var(--heineken-green);
        font-weight: 600;
        font-size: 1.75rem;
        letter-spacing: -0.3px;
    }
    h3 {
        color: var(--heineken-green);
        font-weight: 600;
        font-size: 1.25rem;
    }
    
    /* INPUTS */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        transition: all 0.3s ease;
        padding: 0.75rem;
    }
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {
        border-color: var(--heineken-green);
        box-shadow: 0 0 0 3px rgba(0, 61, 45, 0.1);
    }
    
    /* SELECTBOXES - Dimensiones correctas y texto visible */
    .stSelectbox {
        width: 100% !important;
    }
    /* El contenedor del selectbox de BaseWeb */
    .stSelectbox [data-baseweb="select"] {
        width: 100% !important;
        min-width: 100% !important;
    }
    /* El contenedor interno del select */
    .stSelectbox [data-baseweb="select"] > div {
        width: 100% !important;
        min-width: 100% !important;
        border-radius: 8px;
        border: 2px solid #E0E0E0;
        transition: all 0.3s ease;
    }
    .stSelectbox [data-baseweb="select"] > div:focus-within {
        border-color: var(--heineken-green);
        box-shadow: 0 0 0 3px rgba(0, 61, 45, 0.1);
    }
    /* El área del valor seleccionado - debe tener espacio para el texto y el botón */
    .stSelectbox [data-baseweb="select"] > div > div {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        min-width: 100% !important;
        padding: 0.75rem !important;
    }
    /* El texto seleccionado - debe poder expandirse */
    .stSelectbox [data-baseweb="select"] > div > div > span,
    .stSelectbox [data-baseweb="select"] > div > div > div > span {
        flex: 1 !important;
        white-space: normal !important;
        word-wrap: break-word !important;
        overflow: visible !important;
        text-overflow: clip !important;
        min-width: 0 !important;
        padding-right: 0.5rem !important;
    }
    /* El botón del dropdown - debe mantener su tamaño */
    .stSelectbox [data-baseweb="select"] > div > div > div[role="button"],
    .stSelectbox [data-baseweb="select"] > div > div > svg {
        flex-shrink: 0 !important;
        width: auto !important;
        min-width: 24px !important;
        margin-left: auto !important;
    }
    /* Estilo para el dropdown cuando está abierto */
    .stSelectbox [data-baseweb="popover"] {
        min-width: 200px !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--heineken-green) 0%, var(--heineken-green-light) 100%);
    }
    
    /* CARDS/STEPS */
    .step-card {
        background: white;
        padding: 2.5rem;
        border-radius: 16px;
        box-shadow: var(--card-shadow);
        border-left: 6px solid var(--heineken-green);
        margin-bottom: 2rem;
        transition: all 0.3s ease;
    }
    .step-card:hover {
        box-shadow: 0 12px 32px rgba(0, 61, 45, 0.18);
        transform: translateY(-2px);
    }
    
    /* METRICS */
    [data-testid="stMetricValue"] {
        color: var(--heineken-green);
        font-weight: 700;
    }
    
    /* SUCCESS/INFO/ERROR MESSAGES */
    .stSuccess {
        background: #E8F5E9;
        border-left: 4px solid #4CAF50;
        border-radius: 8px;
    }
    .stInfo {
        background: #E3F2FD;
        border-left: 4px solid #2196F3;
        border-radius: 8px;
    }
    .stError {
        background: #FFEBEE;
        border-left: 4px solid var(--heineken-red);
        border-radius: 8px;
    }
    .stWarning {
        background: #FFF3E0;
        border-left: 4px solid #FF9800;
        border-radius: 8px;
    }
    
    /* RADIO BUTTONS */
    .stRadio > div {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 2px solid #E0E0E0;
    }
    
    /* FILE UPLOADER */
    .stFileUploader > div {
        border: 2px dashed var(--heineken-green);
        border-radius: 12px;
        background: #F9F9F9;
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: var(--heineken-green-light);
        background: #F5F5F5;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE MANAGEMENT ---
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'project_data' not in st.session_state:
    st.session_state.project_data = {}
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'risk_index' not in st.session_state:
    st.session_state.risk_index = 0
if 'recommendation_index' not in st.session_state:
    st.session_state.recommendation_index = 0

# --- HELPER FUNCTIONS ---
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def reset_app():
    st.session_state.step = 1
    st.session_state.project_data = {}
    st.session_state.analysis_result = None
    st.session_state.risk_index = 0
    st.session_state.recommendation_index = 0

# --- CORE LOGIC (Text Extraction, Drive, Gemini) ---
# ... (Reusing robust functions from previous iteration) ...

# GOOGLE DRIVE & DOCS
SCOPE = [
    'https://spreadsheets.google.com/feeds', 
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents'
]
def get_drive_service():
    """Obtiene el servicio de Google Drive con domain-wide delegation si está configurado"""
    if not GOOGLE_SERVICES_AVAILABLE:
        print("❌ Google Services no están disponibles (librerías no instaladas)")
        return None
    if not os.path.exists("credentials.json"):
        print("❌ Archivo credentials.json no encontrado")
        return None
    try:
        creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
        
        # Intentar usar domain-wide delegation si está configurado
        # Esto permite que la cuenta de servicio actúe en nombre de un usuario real
        # que sí tiene cuota de almacenamiento
        user_email = st.secrets.get("GOOGLE_DRIVE_USER_EMAIL", None)
        if user_email:
            print(f"🔐 Usando domain-wide delegation para: {user_email}")
            creds = creds.with_subject(user_email)
        
        service = build('drive', 'v3', credentials=creds)
        print("✅ Servicio de Drive inicializado correctamente")
        return service
    except Exception as e:
        print(f"❌ Error al inicializar servicio de Drive: {e}")
    return None

def test_drive_connection():
    """Función de prueba para verificar la conexión con Google Drive"""
    results = {
        "service_available": False,
        "credentials_file_exists": False,
        "api_enabled": False,
        "folder_accessible": False,
        "error_messages": []
    }
    
    # Verificar si las librerías están disponibles
    if not GOOGLE_SERVICES_AVAILABLE:
        results["error_messages"].append("❌ Google libraries are not installed")
        return results
    
    # Verificar si existe el archivo de credenciales
    if os.path.exists("credentials.json"):
        results["credentials_file_exists"] = True
        print("✅ Archivo credentials.json encontrado")
    else:
        results["error_messages"].append("❌ credentials.json file not found in current directory")
        return results
    
    # Intentar obtener el servicio
    try:
        service = get_drive_service()
        if service:
            results["service_available"] = True
            print("✅ Servicio de Drive creado exitosamente")
        else:
            results["error_messages"].append("❌ Could not create Drive service")
            return results
    except Exception as e:
        results["error_messages"].append(f"❌ Error creating service: {str(e)}")
        return results
    
    # Verificar si la API está habilitada intentando hacer una operación simple
    try:
        # Intentar listar archivos (operación básica)
        about = service.about().get(fields='user,storageQuota').execute()
        results["api_enabled"] = True
        print(f"✅ API de Drive habilitada. Usuario: {about.get('user', {}).get('emailAddress', 'N/A')}")
    except Exception as e:
        error_str = str(e)
        if "403" in error_str or "accessNotConfigured" in error_str or "API has not been used" in error_str:
            results["error_messages"].append("❌ Google Drive API is not enabled. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com")
        else:
            results["error_messages"].append(f"❌ Error verifying API: {error_str}")
        return results
    
    # Verificar acceso a la carpeta raíz o Shared Drive
    try:
        root_id = st.secrets.get("GOOGLE_DRIVE_FOLDER_ID")
        if not root_id:
            results["error_messages"].append("❌ GOOGLE_DRIVE_FOLDER_ID is not set in secrets")
            return results
        
        # Detectar si es Shared Drive (los IDs de Shared Drives empiezan con 0A)
        is_shared_drive = root_id.startswith('0A') and len(root_id) > 10
        
        if is_shared_drive:
            # Para Shared Drives, usar drives().get()
            try:
                drive = service.drives().get(
                    driveId=root_id,
                    fields='id,name'
                ).execute()
                results["folder_accessible"] = True
                print(f"✅ Shared Drive accesible: {drive.get('name', 'N/A')} (ID: {root_id})")
            except Exception as drive_error:
                error_str = str(drive_error)
                if "404" in error_str:
                    results["error_messages"].append(f"❌ Shared Drive with ID '{root_id}' does not exist or the service account is not a member")
                elif "403" in error_str:
                    results["error_messages"].append("❌ No permission. Ensure the service account is a member of the Shared Drive (check your service account email in Google Cloud Console).")
                else:
                    results["error_messages"].append(f"❌ Error accessing Shared Drive: {error_str}")
        else:
            # Para carpetas normales
            folder = service.files().get(
                fileId=root_id,
                fields='id,name,permissions',
                supportsAllDrives=True
            ).execute()
            results["folder_accessible"] = True
            print(f"✅ Carpeta accesible: {folder.get('name', 'N/A')} (ID: {root_id})")
    except Exception as e:
        error_str = str(e)
        if "404" in error_str:
            results["error_messages"].append(f"❌ Folder/Shared Drive with ID '{root_id}' does not exist or you do not have access")
        elif "403" in error_str:
            results["error_messages"].append(f"❌ No permission. Ensure the service account has access")
        else:
            results["error_messages"].append(f"❌ Error accessing: {error_str}")
    
    return results

def find_or_create_folder(drive_service, folder_name, parent_id):
    """Busca o crea una carpeta, soportando Shared Drives"""
    # Detectar si es un Shared Drive (los IDs de Shared Drives empiezan con 0A)
    is_shared_drive = parent_id.startswith('0A') and len(parent_id) > 10
    
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and '{parent_id}' in parents and trashed=false"
    
    # Parámetros necesarios para Shared Drives
    list_params = {
        'q': query,
        'fields': 'files(id)',
        'supportsAllDrives': True,
        'includeItemsFromAllDrives': True
    }
    
    results = drive_service.files().list(**list_params).execute()
    files = results.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        # Crear nueva carpeta
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_id]
        }
        
        # Parámetros para crear en Shared Drive
        create_params = {
            'body': file_metadata,
            'fields': 'id',
            'supportsAllDrives': True
        }
        
        folder = drive_service.files().create(**create_params).execute()
        return folder.get('id')

def upload_file_to_drive(drive_service, file_obj, filename, folder_id, mime_type=None):
    """Sube un archivo a Drive, soportando Shared Drives"""
    media = MediaIoBaseUpload(file_obj, mimetype=mime_type, resumable=True)
    file_metadata = {'name': filename, 'parents': [folder_id]}
    
    # Parámetros necesarios para Shared Drives
    create_params = {
        'body': file_metadata,
        'media_body': media,
        'fields': 'id, webViewLink',
        'supportsAllDrives': True
    }
    
    file = drive_service.files().create(**create_params).execute()
    return file

def create_google_doc(drive_service, title, content, folder_id, im_name):
    """Crea un Google Doc en Drive con el contenido especificado"""
    try:
        from googleapiclient.discovery import build
        from google.oauth2 import service_account
        
        # Obtener credenciales para Docs API
        if os.path.exists("credentials.json"):
            creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
            user_email = st.secrets.get("GOOGLE_DRIVE_USER_EMAIL", None)
            if user_email:
                creds = creds.with_subject(user_email)
            
            docs_service = build('docs', 'v1', credentials=creds)
            
            # Crear el documento vacío
            doc = docs_service.documents().create(body={'title': title}).execute()
            document_id = doc.get('documentId')
            
            # Preparar el contenido del documento con formato
            formatted_content = content
            
            # Insertar contenido en el documento
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': formatted_content
                    }
                }
            ]
            docs_service.documents().batchUpdate(
                documentId=document_id,
                body={'requests': requests}
            ).execute()
            
            # Mover el documento a la carpeta correcta
            file = drive_service.files().get(fileId=document_id, fields='parents', supportsAllDrives=True).execute()
            previous_parents = ",".join(file.get('parents', []))
            
            drive_service.files().update(
                fileId=document_id,
                addParents=folder_id,
                removeParents=previous_parents,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            # Obtener el link del documento
            file_info = drive_service.files().get(
                fileId=document_id,
                fields='id, webViewLink',
                supportsAllDrives=True
            ).execute()
            
            return file_info
        else:
            return None
    except Exception as e:
        print(f"❌ Error al crear Google Doc: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_project_files_to_drive(brand, campaign, influencer, version, files):
    """Guarda archivos en Drive con jerarquía: Campaña -> Influencer -> Versión"""
    if not GOOGLE_SERVICES_AVAILABLE: 
        st.error("❌ Google Services are not available")
        return []
    
    uploaded_links = []
    try:
        print("🔍 Iniciando guardado en Drive...")
        service = get_drive_service()
        root_id = st.secrets.get("GOOGLE_DRIVE_FOLDER_ID")
        
        if not service:
            st.error("⚠️ Could not create Google Drive service. Check credentials.json")
            return []
        
        if not root_id:
            st.error("⚠️ GOOGLE_DRIVE_FOLDER_ID is not set in secrets.toml")
            return []
        
        print(f"📁 Carpeta raíz ID: {root_id}")
        
        # Jerarquía: Campaña -> Influencer -> Versión (sin Brand)
        print(f"📂 Creando estructura: {campaign} -> {influencer} -> {version}")
        camp_id = find_or_create_folder(service, campaign, root_id)
        print(f"✅ Carpeta de campaña creada/encontrada: {camp_id}")
        
        inf_id = find_or_create_folder(service, influencer, camp_id)
        print(f"✅ Carpeta de influencer creada/encontrada: {inf_id}")
        
        ver_id = find_or_create_folder(service, version, inf_id)
        print(f"✅ Carpeta de versión creada/encontrada: {ver_id}")
        
        # Subir archivos a la carpeta de versión
        print(f"📤 Subiendo {len(files)} archivo(s)...")
        for i, (name, data, mime) in enumerate(files, 1):
            try:
                # Asegurar que el objeto de archivo esté en el inicio
                if hasattr(data, 'seek'):
                    data.seek(0)
                print(f"  📄 Subiendo archivo {i}/{len(files)}: {name}")
                f = upload_file_to_drive(service, data, name, ver_id, mime)
                link = f.get('webViewLink', '')
                if link:
                    uploaded_links.append(link)
                    print(f"  ✅ Archivo subido: {link}")
                else:
                    print(f"  ⚠️ Archivo subido pero sin link")
            except Exception as file_error:
                print(f"  ❌ Error al subir {name}: {file_error}")
                st.warning(f"⚠️ Could not upload file {name}: {str(file_error)}")
        
        # Retornar también el link de la carpeta de versión para fácil acceso
        folder_link = f"https://drive.google.com/drive/folders/{ver_id}"
        uploaded_links.insert(0, folder_link)  # Agregar al inicio como link principal
        print(f"✅ Proceso completado. {len(uploaded_links)} link(s) generado(s)")
            
    except Exception as e: 
        error_msg = str(e)
        print(f"Drive Upload Error: {e}")
        
        # Mensaje de error más amigable y específico
        if "403" in error_msg or "accessNotConfigured" in error_msg or "API has not been used" in error_msg:
            st.error("""
            **❌ Error: Google Drive API is not enabled**
            
            To fix this:
            
            1. Go to: https://console.cloud.google.com/apis/library/drive.googleapis.com
            2. Select your project (or create it if it doesn't exist)
            3. Click "ENABLE"
            4. Wait a few minutes and try again
            
            **Note:** Ensure the service account has permissions to access Drive.
            """)
        elif "401" in error_msg or "credentials" in error_msg.lower():
            st.error("""
            **❌ Google Drive authentication error**
            
            Verify that:
            - The `credentials.json` file exists and is valid
            - The service account has permissions in Drive
            - The service account permissions include access to the root folder
            """)
        else:
            st.error(f"""
            **❌ Error uploading files to Drive**
            
            Details: {error_msg}
            
            Check your connection and Google Drive credentials.
            """)
        
    return uploaded_links

# TEXT EXTRACTION
def reconstruct_paragraphs(text):
    """Merges fragmented lines into paragraphs (handles bad PDF/DOCX conversions)."""
    lines = text.split('\n')
    cleaned_lines = []
    buffer = ""
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Only flush if the buffer seems to be a complete sentence/header
            if buffer and buffer.endswith(('.', '!', '?', ':')):
                cleaned_lines.append(buffer)
                buffer = ""
            # Otherwise, assume it's an intra-paragraph break (double spacing) and keep buffer
            continue
            
        # If we have a buffer, check if we should merge
        if buffer:
             buffer += " " + line
        else:
            buffer = line
            
    if buffer: cleaned_lines.append(buffer)
    return "\n".join(cleaned_lines)

def extract_text(uploaded_file):
    try:
        text = ""
        if uploaded_file.name.endswith('.pdf'):
            reader = PdfReader(uploaded_file)
            text = "\n".join([p.extract_text() for p in reader.pages])
        elif uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
        else: # txt
            text = uploaded_file.getvalue().decode("utf-8")
            
        return reconstruct_paragraphs(text), None
    except Exception as e: return None, str(e)

# GEMINI
# GEMINI
def analyze_content(prompt, content):
    api_key = st.secrets.get("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Set temperature to 0.0 for deterministic, consistent results
    config = genai.types.GenerationConfig(temperature=0.0)
    
    return model.generate_content([prompt, content], generation_config=config)

def clean_json_response(text):
    """Robust cleaning for LLM JSON responses."""
    try:
        # Strip markdown code blocks
        clean = text.replace("```json", "").replace("```", "").strip()
        
        # Find JSON boundaries
        start = clean.find("{")
        end = clean.rfind("}")
        if start != -1 and end != -1:
            clean = clean[start:end+1]
            
        # Fix common control character issues
        # Replace actual newlines inside strings with \n is hard without regex, 
        # but often strict=False helps. 
        # For "Invalid control character", we usually need to remove strictly invalid chars 
        # or just hope json.loads(strict=False) works.
        # Let's try raw parsing first, then fallback cleaning.
        return json.loads(clean, strict=False)
    except json.JSONDecodeError:
        # Fallback: Try to escape unescaped control characters
        # This is a naive fix but covers many "newline in string" cases
        import re
        try:
            # Remove control characters that aren't common whitespace
            # clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean) # Too aggressive, removes \n
            return json.loads(clean, strict=False)
        except:
             raise # Re-raise original error if simple strict=False didn't fix it

# DATABASE
def initialize_sheet_headers(sheet):
    """Inicializa los encabezados de la hoja si no existen"""
    try:
        # Verificar si la primera fila está vacía o no tiene encabezados
        first_row = sheet.row_values(1)
        expected_headers = ["Timestamp", "Brand", "Campaign", "Influencer", "Version", "Score", "Recommendations", "Drive Folder Link", "Original File Link", "Report Link"]
        
        if not first_row or first_row != expected_headers:
            if first_row and first_row[0] not in ["Timestamp", "TS"]:
                sheet.clear()
            
            # Agregar encabezados
            sheet.append_row(expected_headers)
            
            # Intentar formatear encabezados usando la API de Sheets directamente
            try:
                spreadsheet = sheet.spreadsheet
                # Obtener el ID de la hoja (gspread expone sheet.id)
                sheet_id = sheet.id
                
                requests = [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 0,
                                "endIndex": 1
                            },
                            "properties": {"pixelSize": 150},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 1,
                                "endIndex": 2
                            },
                            "properties": {"pixelSize": 100},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 2,
                                "endIndex": 3
                            },
                            "properties": {"pixelSize": 200},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 3,
                                "endIndex": 4
                            },
                            "properties": {"pixelSize": 150},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 4,
                                "endIndex": 5
                            },
                            "properties": {"pixelSize": 150},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 5,
                                "endIndex": 6
                            },
                            "properties": {"pixelSize": 80},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 6,
                                "endIndex": 7
                            },
                            "properties": {"pixelSize": 300},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": sheet_id,
                                "dimension": "COLUMNS",
                                "startIndex": 7,
                                "endIndex": 10
                            },
                            "properties": {"pixelSize": 200},
                            "fields": "pixelSize"
                        }
                    },
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": 0,
                                "endRowIndex": 1,
                                "startColumnIndex": 0,
                                "endColumnIndex": len(expected_headers)
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": {"red": 0.0, "green": 0.24, "blue": 0.18},
                                    "textFormat": {
                                        "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
                                        "bold": True,
                                        "fontSize": 11
                                    },
                                    "horizontalAlignment": "CENTER"
                                }
                            },
                            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                        }
                    }
                ]
                
                spreadsheet.batch_update({"requests": requests})
            except Exception as format_error:
                # Si falla el formato avanzado, al menos los encabezados estarán ahí
                print(f"Nota: No se pudo aplicar formato avanzado a los encabezados: {format_error}")
            
    except Exception as e:
        print(f"Error inicializando encabezados: {e}")

def save_db_record(record, drive_links):
    """Guarda registro en Sheets con encabezados y links formateados"""
    sheet_id = st.secrets.get("GOOGLE_SHEET_ID")
    if GOOGLE_SERVICES_AVAILABLE and sheet_id and os.path.exists("credentials.json"):
        try:
            creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=SCOPE)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(sheet_id).sheet1
            
            # Inicializar encabezados si es necesario
            initialize_sheet_headers(sheet)
            
            # Preparar datos de la fila - asegurar que todos sean strings válidos
            def clean_value(value):
                """Limpia un valor para que sea válido en Sheets"""
                if value is None:
                    return ""
                if isinstance(value, (int, float)):
                    return value
                # Convertir a string y limpiar caracteres problemáticos
                value_str = str(value)
                # Reemplazar saltos de línea con espacios para evitar problemas
                value_str = value_str.replace('\n', ' ').replace('\r', ' ')
                # Limitar longitud para evitar problemas (Sheets tiene límite de 50,000 caracteres por celda)
                if len(value_str) > 50000:
                    value_str = value_str[:50000] + "... [truncated]"
                return value_str
            
            timestamp = clean_value(record.get("TS", datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            brand = clean_value(record.get("Brand", ""))
            campaign = clean_value(record.get("Camp", ""))
            influencer = clean_value(record.get("Inf", ""))
            version = clean_value(record.get("Ver", ""))
            score = record.get("Score", 0)
            # Asegurar que score sea un número
            try:
                score = float(score) if score else 0
            except (ValueError, TypeError):
                score = 0
            recs = clean_value(record.get("Recs", ""))
            
            # Extraer links de Drive (el primero es la carpeta, luego archivos)
            folder_link = clean_value(drive_links[0] if len(drive_links) > 0 else "")
            file_link = clean_value(drive_links[1] if len(drive_links) > 1 else "")
            report_link = clean_value(drive_links[2] if len(drive_links) > 2 else "")
            
            # Agregar fila con datos - todos los valores deben ser válidos
            row_data = [
                timestamp,
                brand,
                campaign,
                influencer,
                version,
                score,  # Número
                recs,
                folder_link,
                file_link,
                report_link
            ]
            
            # Verificar que no haya None en los datos
            row_data = ["" if v is None else v for v in row_data]
            
            next_row = sheet.row_count + 1
            sheet.append_row(row_data)
            
            # Formatear links como hipervínculos usando fórmulas HYPERLINK
            # Escapar comillas dobles en los links para evitar errores
            def escape_link(link):
                """Escapa comillas en links para fórmulas HYPERLINK"""
                if not link:
                    return ""
                return link.replace('"', '""')  # Escapar comillas dobles
            
            try:
                if folder_link and folder_link.strip():
                    safe_link = escape_link(folder_link)
                    sheet.update(f'H{next_row}', f'=HYPERLINK("{safe_link}", "📁 Open Folder")', value_input_option='USER_ENTERED')
            except Exception as e:
                print(f"⚠️ No se pudo formatear link de carpeta: {e}")
            
            try:
                if file_link and file_link.strip():
                    safe_link = escape_link(file_link)
                    sheet.update(f'I{next_row}', f'=HYPERLINK("{safe_link}", "📄 View File")', value_input_option='USER_ENTERED')
            except Exception as e:
                print(f"⚠️ No se pudo formatear link de archivo: {e}")
            
            try:
                if report_link and report_link.strip():
                    safe_link = escape_link(report_link)
                    sheet.update(f'J{next_row}', f'=HYPERLINK("{safe_link}", "📊 View Report")', value_input_option='USER_ENTERED')
            except Exception as e:
                print(f"⚠️ No se pudo formatear link de reporte: {e}")
            
            # Formatear la celda de Score con color según el valor
            try:
                score_col = 6  # Columna F (Score)
                score_color = {"red": 0.3, "green": 0.7, "blue": 0.3}  # Verde por defecto
                if score < 60:
                    score_color = {"red": 0.95, "green": 0.3, "blue": 0.3}  # Rojo
                elif score < 90:
                    score_color = {"red": 1.0, "green": 0.8, "blue": 0.4}  # Amarillo/Naranja
                
                spreadsheet = sheet.spreadsheet
                sheet_id = sheet.id
                
                requests = [
                    {
                        "repeatCell": {
                            "range": {
                                "sheetId": sheet_id,
                                "startRowIndex": next_row - 1,
                                "endRowIndex": next_row,
                                "startColumnIndex": score_col - 1,
                                "endColumnIndex": score_col
                            },
                            "cell": {
                                "userEnteredFormat": {
                                    "backgroundColor": score_color,
                                    "textFormat": {"bold": True},
                                    "horizontalAlignment": "CENTER"
                                }
                            },
                            "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                        }
                    }
                ]
                
                spreadsheet.batch_update({"requests": requests})
            except Exception as format_error:
                # Si falla el formato, no es crítico, los datos ya están guardados
                print(f"Nota: No se pudo aplicar formato de color al score: {format_error}")
            
            return True
            
        except Exception as e:
            st.error(f"❌ Error saving to Sheets: {str(e)}")
            print(f"Sheets Save Error: {e}")
            return False
    return False


# PROMPTS (English – AI will respond in English)
PROMPT_F1 = """
Act as an expert in advertising regulations (COFEPRIS) and alcohol for Heineken Mexico.
Your task is to analyse the script looking ONLY for explicit breaches of the law or advertising regulations.

CRITICAL RULES:
1. Do NOT make assumptions or subjective inferences. Only point out what is EXPLICITLY written or described.
2. Example: "Coffee shop" is just a café; do NOT assume drug references unless explicit.
3. If there are no clear risks, state "No risks".
4. Be brief, direct and corporate.
5. Do NOT include invalid control characters in the JSON (tabs, literal newlines inside strings). Use \\n for line breaks.
6. The email must end with "Best regards," followed by the name (the name will be added automatically; do NOT include it in email_draft).

Return ONLY a valid JSON with this exact structure:
{
  "score": number (0-100),
  "risks": [
    {
      "risk": "Short name of the risk",
      "quote": "EXACT verbatim quote from the script where it occurs",
      "explanation": "Legal explanation based on facts, not assumptions"
    }
  ],
  "recommendations": [
    "Concrete action 1",
    "Concrete action 2"
  ],
  "email_draft": "Subject: Script Review - [Campaign]\\n\\nDear team,\\n\\nPlease find attached the findings...\\n\\nBest regards,"
}
"""

PROMPT_F2 = """
Act as Heineken Compliance Officer. Audit the video frame by frame under alcohol regulations (COFEPRIS).
RULES:
1. Only report visual or audio elements that appear in the video.
2. Do NOT infer intentions.
3. Focus on: actual alcohol consumption, minors, driving, excess.

Return ONLY a valid JSON:
{
  "score": number (0-100),
  "risks": [
    {
      "risk": "Visual Risk",
      "timestamp": "MM:SS",
      "explanation": "Observable fact that breaches the regulation"
    }
  ],
  "recommendations": [
    "Required edit 1"
  ],
  "email_draft": "Formal email body"
}
"""

# --- UI LAYOUT ---

# Header with Logo
st.markdown("""
<div style="background: linear-gradient(135deg, #003D2D 0%, #005A47 100%); padding: 2rem 2.5rem; border-radius: 12px; margin-bottom: 2rem; box-shadow: 0 8px 24px rgba(0, 61, 45, 0.2); overflow: hidden;">
    <div style="display: flex; align-items: center; gap: 1.5rem; width: 100%;">
""", unsafe_allow_html=True)

col_logo, col_title = st.columns([1, 6])
with col_logo:
    if os.path.exists("HNKN logo.png"):
        st.image("HNKN logo.png", width=100)
    else:
        st.markdown("## 🍺") 
with col_title:
    st.markdown("""
    <div style="width: 100%; overflow: visible;">
        <h1 style="color: #000000; margin: 0; font-size: 2.5rem; font-weight: 700; letter-spacing: -0.5px; line-height: 1.2;">
            QA Compliance Dashboard
        </h1>
        <p style="color: #1A1A1A; margin: 0.5rem 0 0 0; font-size: 1.1rem; font-weight: 500;">
            AI-Powered Content Analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div></div>", unsafe_allow_html=True)


# --- STEP 1: CONFIGURATION ---
if st.session_state.step == 1:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("1. Project Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        HEINEKEN_BRANDS = ["Heineken", "Tecate", "Dos Equis", "Indio", "Carta Blanca", "Bohemia", "Sol", "Amstel Ultra", "Miller High Life", "Superior"]
        brand = st.selectbox("Brand", HEINEKEN_BRANDS, help="Select the Heineken brand")
        campaign = st.text_input("Campaign Name", placeholder="e.g. Tecate Pa'l Norte 2025", help="Enter the full campaign name")
        influencer = st.text_input("Influencer / Channel", placeholder="e.g. Luisito Comunica", help="Influencer or channel name")
        
    with col2:
        version = st.selectbox("Delivery Version", ["V1 - First Draft", "V2 - Revisions", "V3 - Final", "Published/Witness"], help="Select content version")
        fase = st.radio("Project Phase", ["Phase 1: Script Review (Text)", "Phase 2: Video Audit (MP4)"], horizontal=True)
        im_name = st.text_input("Name of IM performing the review", placeholder="e.g. John Smith", help="Name of the Influencer Marketing person performing this review")
    
    # Nota informativa sobre el ancho de los selectboxes
    st.markdown("""
    <script>
    // Forzar que los selectboxes muestren todo el texto
    setTimeout(function() {
        // Buscar todos los selectboxes
        const selectboxes = document.querySelectorAll('[data-baseweb="select"]');
        selectboxes.forEach(function(select) {
            // Encontrar el span que contiene el texto
            const textSpan = select.querySelector('span');
            if (textSpan) {
                // Forzar estilos inline
                textSpan.style.whiteSpace = 'normal';
                textSpan.style.wordWrap = 'break-word';
                textSpan.style.overflow = 'visible';
                textSpan.style.textOverflow = 'clip';
                textSpan.style.display = 'inline-block';
                textSpan.style.maxWidth = '100%';
            }
            // Asegurar que el contenedor tenga ancho completo
            const container = select.closest('.stSelectbox');
            if (container) {
                container.style.width = '100%';
                container.style.minWidth = '100%';
            }
        });
    }, 100);
    </script>
    """, unsafe_allow_html=True)
    
    # CSS adicional para evitar que los textos se corten
    st.markdown("""
    <style>
        /* SOLUCIÓN ESPECÍFICA PARA SELECTBOXES - Dimensiones correctas */
        /* El contenedor del selectbox de BaseWeb */
        div[data-baseweb="select"] {
            width: 100% !important;
            min-width: 100% !important;
        }
        
        /* El contenedor interno del select */
        div[data-baseweb="select"] > div {
            width: 100% !important;
            min-width: 100% !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* El área del valor seleccionado - debe tener espacio para el texto y el botón */
        div[data-baseweb="select"] > div > div {
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            min-width: 100% !important;
            padding: 0.75rem !important;
        }
        
        /* El texto seleccionado - debe poder expandirse */
        div[data-baseweb="select"] > div > div > span,
        div[data-baseweb="select"] > div > div > div > span {
            flex: 1 !important;
            white-space: normal !important;
            word-wrap: break-word !important;
            overflow: visible !important;
            text-overflow: clip !important;
            min-width: 0 !important;
            padding-right: 0.5rem !important;
            line-height: 1.5 !important;
        }
        
        /* El botón del dropdown - debe mantener su tamaño */
        div[data-baseweb="select"] > div > div > div[role="button"],
        div[data-baseweb="select"] > div > div > svg {
            flex-shrink: 0 !important;
            width: auto !important;
            min-width: 24px !important;
            margin-left: auto !important;
        }
        
        /* Asegurar que las columnas no corten contenido */
        [data-testid="column"] {
            overflow: visible !important;
            min-width: 0 !important;
        }
        
        /* Contenedor de elementos */
        .element-container {
            overflow: visible !important;
            width: 100% !important;
        }
        
        /* Asegurar que los inputs de texto no se corten */
        .stTextInput > div > div > input {
            white-space: normal !important;
            word-wrap: break-word !important;
        }
        
        /* Mejorar visibilidad de labels */
        label {
            font-weight: 600 !important;
            color: #003D2D !important;
            margin-bottom: 0.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("🔧 Verify Google Drive Connection", expanded=False):
        if st.button("🔍 Test Drive Connection"):
            with st.spinner("Verifying connection..."):
                test_results = test_drive_connection()
                
                if test_results["service_available"] and test_results["api_enabled"] and test_results["folder_accessible"]:
                    st.success("✅ Google Drive connection successful! Everything is set up correctly.")
                else:
                    st.error("❌ There are problems with the Google Drive connection:")
                    for error in test_results["error_messages"]:
                        st.error(error)
                    
                    cred_status = "✅" if test_results['credentials_file_exists'] else "❌"
                    service_status = "✅" if test_results['service_available'] else "❌"
                    api_status = "✅" if test_results['api_enabled'] else "❌"
                    folder_status = "✅" if test_results['folder_accessible'] else "❌"
                    
                    st.info(f"""
                    **Verification summary:**
                    - Credentials: {cred_status}
                    - Service available: {service_status}
                    - API enabled: {api_status}
                    - Folder accessible: {folder_status}
                    """)
    
    st.markdown("---")
    
    uploaded_file = None
    if "Phase 1" in fase:
        uploaded_file = st.file_uploader("Upload Script (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
    else:
        uploaded_file = st.file_uploader("Upload Video (MP4, MOV)", type=['mp4', 'mov'])
        
    if st.button("Start Analysis ▶️"):
        if campaign and influencer and uploaded_file:
            st.session_state.project_data = {
                "brand": brand,
                "campaign": campaign,
                "influencer": influencer,
                "version": version,
                "im_name": im_name,
                "type": "script" if "Phase 1" in fase else "video",
                "file": uploaded_file
            }
            # Run Analysis immediately to transition
            with st.spinner("Processing with Gemini AI..."):
                if "Phase 1" in fase:
                    txt, err = extract_text(uploaded_file)
                    if txt:
                        # Clean text for better matching
                        txt = txt.replace("\r", "")
                        resp = analyze_content(PROMPT_F1, txt)
                        print(f"DEBUG: Raw AI Response (Text): {resp.text}")
                        try:
                            st.session_state.analysis_result = clean_json_response(resp.text)
                            next_step()
                            st.rerun()
                        except Exception as e:
                            print(f"DEBUG: Parsing Error: {e}")
                            st.error(f"Error interpreting AI response: {e}")
                            st.code(resp.text, language='json')
                else:
                    # Video Logic – configure Gemini API key before upload (upload_file needs it)
                    api_key = st.secrets.get("GEMINI_API_KEY")
                    if not api_key:
                        st.error("GEMINI_API_KEY is not set in Secrets. Add it in Streamlit Cloud → Settings → Secrets.")
                        st.stop()
                    genai.configure(api_key=api_key)
                    with open("temp_vid.mp4", "wb") as f: f.write(uploaded_file.getbuffer())
                    st.info("Uploading video to Gemini...")
                    vid_upload = genai.upload_file("temp_vid.mp4")
                    # Poll for processing completion
                    with st.spinner(f"Processing video... (Initial state: {vid_upload.state.name})"):
                        while vid_upload.state.name == "PROCESSING":
                            time.sleep(5)
                            vid_upload = genai.get_file(vid_upload.name)
                    if vid_upload.state.name == "FAILED":
                        st.error("Video processing failed on Gemini.")
                        st.stop()
                    resp = analyze_content(PROMPT_F2, vid_upload)
                    print(f"DEBUG: Raw AI Response (Video): {resp.text}")
                    try:
                        st.session_state.analysis_result = clean_json_response(resp.text)
                        next_step()
                        st.rerun()
                    except Exception as e:
                        print(f"DEBUG: Parsing Error: {e}")
                        st.error(f"Error interpreting AI response: {e}")
                        st.code(resp.text, language='json')
        else:
            st.warning("Please complete all fields")
    st.markdown('</div>', unsafe_allow_html=True)


# --- STEP 2: REVIEW & EDIT ---
elif st.session_state.step == 2:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("2. Review and Edit Findings")
    
    col_left, col_right = st.columns([1, 1])
    
    data = st.session_state.analysis_result
    p_data = st.session_state.project_data
    risks = data.get('risks', [])
    recs = data.get('recommendations', [])
    
    with col_left:
        st.markdown("#### 📄 Original Material")
        if p_data['type'] == 'script':
             txt, _ = extract_text(p_data['file'])
             
             
             # Highlight Logic
             # We will re-process the text to make it look like a script
             import re
             
             def format_script_line(line):
                line = line.strip()
                if not line: return "<br>" # Single break for empty lines
                
                # Check for Speaker (e.g., "LUISITO:", "Narrador - ", "LUISITO (en off):")
                # Heuristic: Uppercase words at start followed by colon or dash
                # Relaxed regex: Allow parens inside speaker name, match start of line
                match = re.match(r'^([A-ZÁÉÍÓÚÑ\s\(\)]{2,30})(:|-)', line)
                if match:
                    speaker = match.group(1)
                    rest = line[len(speaker):]
                    # Bold the speaker
                    return f'<div style="margin-top: 10px; margin-bottom: 4px;"><strong>{speaker}</strong>{rest}</div>'
                
                # Check for Scene Headers or Camera Directions (often Uppercase)
                # If line is short and mostly uppercase
                if len(line) < 50 and line.isupper():
                     return f'<div style="margin-top: 15px; margin-bottom: 5px; font-weight: bold; color: #555; text-decoration: underline;">{line}</div>'

                # Check for Questions (Interview style)
                if line.endswith("?"):
                     return f'<div style="margin-bottom: 8px; font-weight: bold; color: #008200;">{line}</div>'
                
                # Normal text
                return f'<div style="margin-bottom: 8px; margin-left: 10px;">{line}</div>'
                


             formatted_html = ""
             lines = txt.split('\n')
             for line in lines:
                 formatted_html += format_script_line(line)
             
             # Apply Highlights on top of the formatted HTML?
             # It's risky to replace inside HTML tags. 
             # Safe approach: Replace exact text content.
             # Given the structure, simple string replace might break div tags if regex matches them.
             # We will try a careful replace or just highlight the raw text logic differently.
             # Let's try matching the text content.
             
             for i, r in enumerate(risks):
                 quote = r.get('quote', '').strip()
                 if quote:
                     # We need to escape special regex chars to avoid errors
                     safe_quote = re.escape(quote)
                     # highlighting style
                     span = f'<span style="background-color: #ffdce0; border-bottom: 2px solid #ff2a2a;">{quote}</span>'
                     # Replace only non-tag text? Difficult with simple regex. 
                     # Let's trust that quotes are usually unique enough or don't match HTML tags.
                     formatted_html = re.sub(safe_quote, span, formatted_html, flags=re.IGNORECASE)
             
             st.markdown(
                 f"""
                 <div style="height: 600px; overflow-y: scroll; padding: 30px; background: #fafafa; border: 1px solid #ddd; border-radius: 8px; font-family: 'Verdana', sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
                    {formatted_html}
                 </div>
                 """, 
                 unsafe_allow_html=True
             )
        else:
             st.video(p_data['file'])
             
    with col_right:
        score = data.get('score', 0)
        score_color = "red" if score < 60 else "orange" if score < 90 else "green"
        st.markdown(f"#### 🛡️ Compliance Score: <span style='color:{score_color}; font-size: 1.2em;'>{score}/100</span>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # RISKS SECTION
        st.markdown("### 🚨 Detected Risks")
        if not risks:
            st.success("No critical risks detected.")
        else:
             # Carousel Logic
             current_idx = st.session_state.risk_index
             total_risks = len(risks)
             
             # Bounds Check (just in case)
             if current_idx >= total_risks: current_idx = 0
             if current_idx < 0: current_idx = total_risks - 1
             st.session_state.risk_index = current_idx
            
             r = risks[current_idx]
             
             # Navigation Buttons
             col_prev, col_info, col_next = st.columns([1, 4, 1])
             with col_prev:
                 if st.button("⬅️", key="prev_risk"):
                     st.session_state.risk_index = (current_idx - 1) % total_risks
                     st.rerun()
             with col_next:
                 if st.button("➡️", key="next_risk"):
                     st.session_state.risk_index = (current_idx + 1) % total_risks
                     st.rerun()
             with col_info:
                 st.markdown(f"<div style='text-align: center; color: #555;'>Risk {current_idx + 1} of {total_risks}</div>", unsafe_allow_html=True)
             
             # Risk Card (Current)
             risk_title = r.get('risk', 'Risk')
             risk_expl = r.get('explanation', '')
             risk_ts = r.get('timestamp', '')
            
             st.markdown(
                 f"""
                 <div style="background: #fff8f8; border-left: 5px solid #ff2a2a; padding: 15px; border-radius: 5px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <h4 style="color: #d30000; margin-top: 0;">{risk_title}</h4>
                    <p style="font-size: 14px; color: #333;">{risk_expl}</p>
                 </div>
                 """, 
                 unsafe_allow_html=True
             )
             
             if p_data['type'] == 'script' and r.get('quote'):
                 st.markdown(f"**Quote:** *\"{r.get('quote')}\"*")
             elif p_data['type'] == 'video' and risk_ts:
                 st.markdown(f"⏱ **Time:** {risk_ts}")
        
        st.markdown("---")
        
        # RECOMMENDATIONS SECTION
        st.markdown("### 💡 Recommendations")
        
        if not recs:
             st.info("No specific recommendations.")
             joined_recs = ""
        else:
             # Carousel Logic
             current_rec_idx = st.session_state.recommendation_index
             total_recs = len(recs)
             
             # Bounds Check
             if current_rec_idx >= total_recs: current_rec_idx = 0
             if current_rec_idx < 0: current_rec_idx = total_recs - 1
             st.session_state.recommendation_index = current_rec_idx
             
             rec = recs[current_rec_idx]
             
             # Navigation Buttons
             col_r_prev, col_r_info, col_r_next = st.columns([1, 4, 1])
             with col_r_prev:
                 if st.button("⬅️", key="prev_rec"):
                     st.session_state.recommendation_index = (current_rec_idx - 1) % total_recs
                     st.rerun()
             with col_r_next:
                 if st.button("➡️", key="next_rec"):
                     st.session_state.recommendation_index = (current_rec_idx + 1) % total_recs
                     st.rerun()
             with col_r_info:
                 st.markdown(f"<div style='text-align: center; color: #555;'>Recommendation {current_rec_idx + 1} of {total_recs}</div>", unsafe_allow_html=True)
            
             # Recommendation Card
             st.info(rec, icon="✅")
             
             joined_recs = "\n".join([f"- {r}" for r in recs])
            
        # Editable Compilation
        st.markdown("**Final Edit (for report/email):**")
        edited_recs = st.text_area("Adjust recommendations:", 
                                   value=joined_recs, 
                                   height=150,
                                   key="final_recs_input")
        
        st.session_state.analysis_result['final_recs'] = edited_recs
        
        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if st.button("⬅️ Back"): prev_step(); st.rerun()
        with col_act2:
            if st.button("Approve and Draft Email ✅"): next_step(); st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)


# --- STEP 3: FINALIZE ---
elif st.session_state.step == 3:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.subheader("3. Confirmation and Submit")
    
    data = st.session_state.analysis_result
    
    st.success("✅ Analysis completed and saved")
    
    st.markdown("#### ✉️ Email Preview")
    
    # Check if 'email_draft' from AI is plain text or structured.
    # We'll augment it to be HTML-like for display, but keep plain text for editing/clipboard?
    # Actually, let's allow editing rich text if possible, but Streamlit only has plain text area.
    # We will provide a styled HTML preview and a raw text editor.
    
    raw_email = data.get('email_draft', '')
    
    col_preview, col_edit = st.columns(2)
    
    with col_edit:
        st.markdown("**📝 Edit Content:**")
        im_name = st.session_state.project_data.get('im_name', 'QA Team')
        if raw_email and not raw_email.strip().endswith('Best regards,'):
            if not raw_email.strip().endswith('Best regards'):
                raw_email = raw_email.rstrip() + "\n\nBest regards,"
        email_body = st.text_area("Email body:", value=raw_email, height=400)
    
    with col_preview:
        st.markdown("**👁️ Preview (Simulated):**")
        # Turn newlines into breaks for HTML preview
        html_preview = email_body.replace("\n", "<br>")
        st.markdown(
            f"""
            <div style="background: white; border: 1px solid #ccc; padding: 20px; border-radius: 5px; font-family: Arial, sans-serif; font-size: 14px; color: #333;">
                <div style="border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 10px;">
                    <strong>Subject:</strong> Content Review - {st.session_state.project_data.get('campaign', 'Campaign')}
                </div>
                {html_preview}
                <br><br>
                <div style="color: #666; font-size: 12px; border-top: 1px solid #eee; padding-top: 10px;">
                    <em>Generated by Heineken QA Copilot</em>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    if st.button("Confirm and Save All 💾"):
        # Guardar archivos localmente como respaldo
        local_files_path = []
        
        # Save to Drive
        files = []
        p_data = st.session_state.project_data
        p_data['file'].seek(0)
        file_content = p_data['file'].read()
        files.append((p_data['file'].name, io.BytesIO(file_content), p_data['file'].type))
        
        # Guardar archivo original localmente
        try:
            os.makedirs("archivos_guardados", exist_ok=True)
            local_file_path = f"archivos_guardados/{p_data['campaign']}_{p_data['influencer']}_{p_data['version']}_{p_data['file'].name}"
            with open(local_file_path, 'wb') as f:
                f.write(file_content)
            local_files_path.append(local_file_path)
        except Exception as e:
            print(f"⚠️ No se pudo guardar archivo localmente: {e}")
        
        im_name = p_data.get('im_name', 'QA Team')
        
        doc_content = (
            f"REVIEW REPORT - {p_data['campaign']}\n\n"
            f"PROJECT INFORMATION\n"
            f"{'='*80}\n"
            f"Brand: {p_data['brand']}\n"
            f"Campaign: {p_data['campaign']}\n"
            f"Influencer: {p_data['influencer']}\n"
            f"Version: {p_data['version']}\n"
            f"Score: {data.get('score', 0)}/100\n"
            f"Reviewed by: {im_name}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"RECOMMENDATIONS\n"
            f"{'='*80}\n"
            f"{st.session_state.analysis_result['final_recs']}\n\n"
            f"FINAL EMAIL\n"
            f"{'='*80}\n"
            f"{email_body}\n\n"
            f"Best regards,\n{im_name}\n"
        )
        
        # Crear Google Doc en lugar de JSON
        service = get_drive_service()
        report_link = ""
        if service:
            # Obtener la carpeta de versión
            root_id = st.secrets.get('GOOGLE_DRIVE_FOLDER_ID')
            if root_id:
                camp_id = find_or_create_folder(service, p_data['campaign'], root_id)
                inf_id = find_or_create_folder(service, p_data['influencer'], camp_id)
                ver_id = find_or_create_folder(service, p_data['version'], inf_id)
                
                # Crear el Google Doc
                doc_title = f"Reporte_{p_data['version']}_{p_data['campaign']}"
                doc_file = create_google_doc(service, doc_title, doc_content, ver_id, im_name)
                if doc_file:
                    report_link = doc_file.get('webViewLink', '')
                    if report_link:
                        links.append(report_link)
                        print(f"✅ Google Doc creado: {report_link}")
        
        # Guardar archivo original y Google Doc en Drive con jerarquía Campaña-Influencer-Versión
        links = []
        drive_success = False
        try:
            with st.spinner("💾 Saving files to Google Drive..."):
                links = save_project_files_to_drive(p_data['brand'], p_data['campaign'], p_data['influencer'], p_data['version'], files)
            
            if links and len(links) > 0:
                st.success(f"✅ Files saved to Drive. {len(links)} file(s) uploaded.")
                drive_success = True
            else:
                st.warning("⚠️ Files could not be uploaded to Drive, but the record will be saved to Sheets.")
        except Exception as drive_error:
            error_str = str(drive_error)
            if "storageQuotaExceeded" in error_str or "Service Accounts do not have storage quota" in error_str:
                warning_msg = (
                    "**Cannot upload files to Drive**\n\n"
                    "Service accounts do not have storage quota. To fix this:\n\n"
                    "**Option 1 (Recommended):** Ask your Google Workspace admin to:\n"
                    "1. Enable \"Domain-wide delegation\" for the service account\n"
                    "2. Configure the required scopes in Google Workspace Admin Console\n\n"
                    "**Option 2:** Files will be saved locally. You can upload them to Drive manually later.\n\n"
                    "The record will be saved to Sheets with all analysis information."
                )
                st.warning(warning_msg)
            else:
                st.warning(f"⚠️ Error saving to Drive: {str(drive_error)}. Continuing with saving to Sheets...")
            links = []
        
        # Agregar el link del Google Doc a la lista de links si se creó
        if report_link:
            links.append(report_link)
        
