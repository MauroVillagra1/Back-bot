"""
Dependencias reutilizables de FastAPI para autenticación y autorización (RBAC).

Jerarquía de roles (de mayor a menor privilegio):
  root > master > administrativo / jefe_area / docente > estudiante

Tabla de permisos:
  root           → todo (incluye editar/eliminar usuarios y crear masters)
  master         → crear usuarios, suspensiones, material, info cursado, eventos, resumen, chat
  administrativo → eventos globales + chat
  jefe_area      → suspensiones de su área + resumen de su área + chat
  docente        → suspensiones/material/info de sus cursadas + chat
  estudiante     → solo chat
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token

http_bearer = HTTPBearer()

# ── Grupos de roles (strings para comparación flexible con aliases legacy) ────

# Acceso total
_ROLES_ROOT = {"root"}

# Master y superiores (root tiene todo lo de master)
_ROLES_MASTER = {"root", "master", "administrador"}

# Pueden gestionar calendario/eventos globales
_ROLES_CALENDARIO = {"root", "master", "administrador", "administrativo"}

# Pueden crear/gestionar cursadas (estructura académica)
_ROLES_ACAD_ADMIN = {
    "root", "master", "administrador",
    "jefe_area", "jefe_departamento",
}

# Docentes y superiores
_ROLES_DOCENTE = {
    "root", "master", "administrador",
    "jefe_area", "jefe_departamento",
    "docente", "profesor", "profesor_directivo",
}

# Todo el staff (cualquiera excepto estudiante/alumno)
_ROLES_STAFF = {
    "root", "master", "administrador",
    "administrativo",
    "jefe_area", "jefe_departamento",
    "docente", "profesor", "profesor_directivo",
}


# ── Dependencia base ──────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(http_bearer),
    db: Session = Depends(get_db),
):
    from app.models.usuario import Usuario

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.get(Usuario, int(user_id))
    if user is None:
        raise credentials_exception
    if not user.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo",
        )
    return user


# ── Fábrica de dependencias RBAC ──────────────────────────────────────────────

def require_rol(*roles: str):
    """
    Fábrica: devuelve una dependencia FastAPI que verifica que el usuario
    autenticado tenga uno de los roles especificados.
    Acepta tanto los roles nuevos como los aliases legacy.
    """
    role_set = set(roles)

    def _dependency(current_user=Depends(get_current_user)):
        if current_user.rol.value not in role_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Se requiere uno de los roles: {', '.join(sorted(role_set))}",
            )
        return current_user

    return _dependency


# ── Dependencias pre-construidas ──────────────────────────────────────────────

# Cualquier usuario autenticado (incluyendo estudiante)
require_authenticated = get_current_user

# Solo root
require_root = require_rol(*_ROLES_ROOT)

# Master y superiores (root + master + alias administrador)
require_master = require_rol(*_ROLES_MASTER)

# Puede gestionar eventos de calendario globales
require_calendario = require_rol(*_ROLES_CALENDARIO)

# Puede gestionar estructura académica (crear cursadas, asignar profesores)
require_acad_admin = require_rol(*_ROLES_ACAD_ADMIN)

# Docentes y superiores (para material, info cursada, excepciones)
require_docente = require_rol(*_ROLES_DOCENTE)

# Todo el staff (no estudiante)
require_staff = require_rol(*_ROLES_STAFF)

# alias legacy
require_admin   = require_master
require_profesor = require_docente
