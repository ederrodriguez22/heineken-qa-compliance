# Solución para el Error de Cuota de Almacenamiento en Drive

## Problema
Las cuentas de servicio de Google no tienen cuota de almacenamiento propia. Cuando intentas subir archivos, obtienes el error:
```
Service Accounts do not have storage quota
```

## Soluciones

### Opción 1: Domain-Wide Delegation (Recomendada - Requiere Google Workspace Admin)

Esta solución permite que la cuenta de servicio actúe en nombre de un usuario real.

#### Pasos:

1. **Habilitar Domain-Wide Delegation en la cuenta de servicio:**
   - Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Selecciona tu proyecto
   - Encuentra la cuenta de servicio: `compliance-bot@stellar-depth-382121.iam.gserviceaccount.com`
   - Haz clic en "Editar"
   - Activa "Habilitar delegación de todo el dominio de Google Workspace"
   - Guarda

2. **Agregar el email del usuario en secrets.toml:**
   ```toml
   GOOGLE_DRIVE_USER_EMAIL = "tu-email@tudominio.com"
   ```

3. **El código ya está actualizado** para usar domain-wide delegation si está configurado.

### Opción 2: Usar Shared Drive (Google Workspace)

Si tienes Google Workspace, puedes crear un Shared Drive y la cuenta de servicio puede subir archivos allí.

1. Crea un Shared Drive en Google Workspace
2. Agrega la cuenta de servicio como miembro con permisos de "Editor"
3. Usa el ID del Shared Drive en lugar de una carpeta normal

### Opción 3: Subir a Carpeta Compartida del Usuario (Solución Temporal)

Si no tienes acceso de administrador, puedes:

1. Crear una carpeta en TU Drive personal
2. Compartirla con la cuenta de servicio
3. La cuenta de servicio puede subir archivos a esa carpeta compartida

**Nota:** Esta opción puede tener limitaciones dependiendo de la configuración.

## Configuración Actual

El código ya está preparado para usar domain-wide delegation. Solo necesitas:

1. Habilitar domain-wide delegation en Google Cloud Console (requiere admin)
2. Agregar `GOOGLE_DRIVE_USER_EMAIL` en `.streamlit/secrets.toml`

## Verificación

Después de configurar, ejecuta:
```bash
python3 diagnostico_drive.py
```

Si todo está bien, deberías poder subir archivos sin problemas de cuota.


