"""
Router para MaterialApoyo — apuntes, videos, links, etc.

Permisos:
  - Cargar:   docente (solo sus cursadas) / master (cualquier cursada)
  - Leer:     cualquier usuario autenticado (estudiantes filtrados a su comisión)
  - Eliminar: quien lo cargó, o master/root
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_docente
from app.models.cursada import Cursada, CursadaProfesor
from app.models.material import MaterialApoyo, TipoMaterialEnum
from app.models.usuario import Usuario

router = APIRouter(prefix="/materiales", tags=["Materiales de apoyo"])

_ROLES_FULL_ACCESS = {"root", "master", "administrador"}


class MaterialCreate(BaseModel):
    cursada_id: int
    tipo: TipoMaterialEnum
    titulo: str = Field(..., min_length=2, max_length=255)
    url: str | None = None
    descripcion: str | None = None


class MaterialRead(BaseModel):
    id: int
    cursada_id: int
    tipo: TipoMaterialEnum
    titulo: str
    url: str | None
    descripcion: str | None
    cargado_por: int

    model_config = {"from_attributes": True}


@router.post("/", response_model=MaterialRead, status_code=201)
def cargar_material(
    data: MaterialCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_docente),
):
    """
    Carga material a una cursada.
    Docentes solo pueden subir a cursadas donde están asignados.
    Master/root pueden subir a cualquier cursada.
    """
    cursada = db.get(Cursada, data.cursada_id)
    if not cursada:
        raise HTTPException(status_code=404, detail="Cursada no encontrada")

    # Docentes: verificar que sean de esa cursada
    if current_user.es_docente and current_user.rol.value not in _ROLES_FULL_ACCESS:
        asignado = db.query(CursadaProfesor).filter(
            CursadaProfesor.cursada_id == data.cursada_id,
            CursadaProfesor.profesor_id == current_user.id,
        ).first()
        if not asignado:
            raise HTTPException(
                status_code=403,
                detail="Solo podés cargar material en cursadas donde estás asignado como docente",
            )

    obj = MaterialApoyo(**data.model_dump(), cargado_por=current_user.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.get("/cursada/{cursada_id}", response_model=list[MaterialRead])
def listar_materiales(
    cursada_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    cursada = db.get(Cursada, cursada_id)
    if not cursada:
        raise HTTPException(status_code=404, detail="Cursada no encontrada")

    if current_user.es_estudiante:
        comisiones = [uc.comision_id for uc in current_user.comisiones]
        if cursada.comision_id not in comisiones:
            raise HTTPException(status_code=403, detail="Sin acceso a esta cursada")

    return db.query(MaterialApoyo).filter(MaterialApoyo.cursada_id == cursada_id).all()


@router.delete("/{material_id}", status_code=204)
def eliminar_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_docente),
):
    """Solo puede eliminar quien lo cargó, o master/root."""
    obj = db.get(MaterialApoyo, material_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Material no encontrado")

    es_autor = obj.cargado_por == current_user.id
    es_privilegiado = current_user.rol.value in _ROLES_FULL_ACCESS

    if not es_autor and not es_privilegiado:
        raise HTTPException(status_code=403, detail="Solo podés eliminar material que vos cargaste")

    db.delete(obj)
    db.commit()
