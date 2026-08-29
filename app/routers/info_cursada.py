"""
Router InfoCursada — docente carga/actualiza la info de su cursada:
condiciones de aprobación, parciales, TFI, modalidad, etc.

Permisos:
  - PUT (crear/actualizar): docente asignado a esa cursada, o master/root
  - GET: cualquier usuario autenticado
  - DELETE: quien lo cargó, o master/root
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_docente
from app.models.cursada import CursadaProfesor
from app.models.info_cursada import InfoCursada
from app.models.usuario import Usuario

router = APIRouter(prefix="/info-cursada", tags=["Info del cursado"])

_ROLES_FULL_ACCESS = {"root", "master", "administrador"}


class InfoCursadaPayload(BaseModel):
    cursada_id: int
    condiciones_aprobacion: str | None = None
    cantidad_parciales: int | None = None
    tiene_tfi: bool | None = False
    descripcion_tfi: str | None = None
    modalidad_cursado: str | None = None
    info_adicional: str | None = None


class InfoCursadaRead(InfoCursadaPayload):
    id: int
    cargado_por: int
    model_config = {"from_attributes": True}


def _verificar_acceso_docente(cursada_id: int, usuario: Usuario, db: Session) -> None:
    """Verifica que el docente esté asignado a la cursada. Master/root bypasean."""
    if usuario.rol.value in _ROLES_FULL_ACCESS:
        return
    if usuario.es_jefe:
        return  # jefe_area puede ver info de su área
    asignado = db.query(CursadaProfesor).filter(
        CursadaProfesor.cursada_id == cursada_id,
        CursadaProfesor.profesor_id == usuario.id,
    ).first()
    if not asignado:
        raise HTTPException(
            status_code=403,
            detail="Solo podés cargar info en cursadas donde estás asignado como docente",
        )


@router.put("/{cursada_id}", response_model=InfoCursadaRead)
def guardar_info(
    cursada_id: int,
    data: InfoCursadaPayload,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_docente),
):
    """Crea o actualiza la info del cursado (upsert). Solo el docente asignado o master/root."""
    if data.cursada_id != cursada_id:
        raise HTTPException(status_code=422, detail="cursada_id no coincide")

    _verificar_acceso_docente(cursada_id, current_user, db)

    obj = db.query(InfoCursada).filter(InfoCursada.cursada_id == cursada_id).first()
    if obj:
        for field, value in data.model_dump(exclude={"cursada_id"}).items():
            setattr(obj, field, value)
        obj.cargado_por = current_user.id
    else:
        obj = InfoCursada(**data.model_dump(), cargado_por=current_user.id)
        db.add(obj)

    try:
        db.commit()
        db.refresh(obj)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Error al guardar la información")

    return obj


@router.get("/{cursada_id}", response_model=InfoCursadaRead | None)
def obtener_info(
    cursada_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    """Devuelve la info del cursado. Visible para cualquier usuario autenticado."""
    return db.query(InfoCursada).filter(InfoCursada.cursada_id == cursada_id).first()


@router.delete("/{cursada_id}", status_code=204)
def eliminar_info(
    cursada_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_docente),
):
    """Elimina la info del cursado. Solo quien la cargó o master/root."""
    obj = db.query(InfoCursada).filter(InfoCursada.cursada_id == cursada_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Info no encontrada")

    es_autor = obj.cargado_por == current_user.id
    es_privilegiado = current_user.rol.value in _ROLES_FULL_ACCESS

    if not es_autor and not es_privilegiado:
        raise HTTPException(status_code=403, detail="Solo podés eliminar info que vos cargaste")

    db.delete(obj)
    db.commit()
