"""
Router de usuarios (gestión de cuentas).

Permisos:
  - Crear usuarios (A, J, D, E):  master y superiores
  - Deshabilitar (banear):        master y superiores
  - Listar / ver detalle:         master y superiores
  - Actualizar datos:             master y superiores
  - Eliminar / crear masters:     solo root
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_master, require_root, get_current_user
from app.core.security import hash_password
from app.models.usuario import RolEnum, Usuario
from app.schemas.common import PaginatedResponse
from app.schemas.usuario import UsuarioCreate, UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

# Roles que master puede crear (no puede crear root ni otro master)
_ROLES_CREABLES_POR_MASTER = {
    RolEnum.administrativo,
    RolEnum.jefe_area,
    RolEnum.docente,
    RolEnum.estudiante,
}
# Solo root puede crear master
_ROLES_SOLO_ROOT = {RolEnum.root, RolEnum.master}


@router.post("/", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    data: UsuarioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_master),
):
    """
    Crea un nuevo usuario.
    - Master puede crear: administrativo, jefe_area, docente, estudiante.
    - Root puede crear cualquier rol incluido master.
    """
    # Verificar que master no intente crear root/master
    if data.rol in _ROLES_SOLO_ROOT and not current_user.es_root:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo root puede crear usuarios con rol master o root",
        )

    if db.query(Usuario).filter(Usuario.email == data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    usuario = Usuario(
        nombre=data.nombre,
        apellido=data.apellido,
        email=data.email,
        rol=data.rol,
        fecha_nacimiento=data.fecha_nacimiento,
        password_hash=hash_password(data.password),
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.get("/", response_model=PaginatedResponse[UsuarioRead])
def listar_usuarios(
    rol: str | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    _=Depends(require_master),
):
    """Lista todos los usuarios con paginación. Master y superiores."""
    offset = (page - 1) * page_size
    query = db.query(Usuario)
    if rol:
        query = query.filter(Usuario.rol == rol)
    total = query.count()
    usuarios = query.offset(offset).limit(page_size).all()
    return PaginatedResponse(items=usuarios, total=total, page=page, page_size=page_size)


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_master),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router.patch("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int,
    data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_master),
):
    """
    Actualiza campos de un usuario.
    - Master no puede cambiar el rol a master/root.
    - Solo root puede desactivar/activar a otro master.
    """
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    # Master no puede tocar a otro master o root
    if not current_user.es_root and usuario.es_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo root puede modificar usuarios master o root",
        )

    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = hash_password(update_data.pop("password"))

    # Validar que master no cambie rol a master/root
    if "rol" in update_data and not current_user.es_root:
        if update_data["rol"] in (RolEnum.root.value, RolEnum.master.value):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo root puede asignar rol master o root",
            )

    for field, value in update_data.items():
        setattr(usuario, field, value)

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_root),
):
    """Elimina un usuario permanentemente. Solo root."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()


@router.patch("/{usuario_id}/deshabilitar", response_model=UsuarioRead)
def deshabilitar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_master),
):
    """Desactiva (banea) a un usuario. Master y superiores."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if not current_user.es_root and usuario.es_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo root puede deshabilitar a un master",
        )

    usuario.activo = False
    db.commit()
    db.refresh(usuario)
    return usuario


@router.patch("/{usuario_id}/habilitar", response_model=UsuarioRead)
def habilitar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_master),
):
    """Reactiva a un usuario deshabilitado. Master y superiores."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    if not current_user.es_root and usuario.es_master:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo root puede habilitar a un master",
        )

    usuario.activo = True
    db.commit()
    db.refresh(usuario)
    return usuario
