"""
Modelo Usuario — representa a cualquier persona del sistema.

Roles (de mayor a menor privilegio):
  - root             → acceso total, puede editar/eliminar usuarios, crear masters
  - master           → gestión completa excepto root-only
  - administrativo   → solo eventos de calendario globales + chat
  - jefe_area        → suspensiones/reubicaciones de su área + resumen + chat
  - docente          → gestión de sus cursadas + chat
  - estudiante       → solo chat
"""
import enum
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class RolEnum(str, enum.Enum):
    root           = "root"
    master         = "master"
    administrativo = "administrativo"
    jefe_area      = "jefe_area"
    docente        = "docente"
    estudiante     = "estudiante"

    # ── aliases legacy para no romper datos existentes en la BD ──────────────
    administrador     = "administrador"       # → se trata como master
    jefe_departamento = "jefe_departamento"   # → se trata como jefe_area
    profesor          = "profesor"            # → se trata como docente
    profesor_directivo = "profesor_directivo" # → se trata como docente
    alumno            = "alumno"              # → se trata como estudiante


class Usuario(Base):
    __tablename__ = "usuarios"

    id:            Mapped[int]      = mapped_column(primary_key=True, index=True)
    nombre:        Mapped[str]      = mapped_column(String(100), nullable=False)
    apellido:      Mapped[str | None] = mapped_column(String(100), nullable=True)
    email:         Mapped[str]      = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str]      = mapped_column(String(255), nullable=False)
    rol:           Mapped[RolEnum]  = mapped_column(Enum(RolEnum, name="rolenum"), nullable=False)
    activo:        Mapped[bool]     = mapped_column(Boolean, default=True, nullable=False)
    fecha_nacimiento: Mapped[date | None] = mapped_column(Date, nullable=True)

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relaciones ────────────────────────────────────────────────────────────
    comisiones: Mapped[list["UsuarioComision"]] = relationship(
        "UsuarioComision", back_populates="usuario", cascade="all, delete-orphan"
    )
    cursadas_como_profesor: Mapped[list["CursadaProfesor"]] = relationship(
        "CursadaProfesor", back_populates="profesor", cascade="all, delete-orphan"
    )

    # ── Helpers de rol ────────────────────────────────────────────────────────
    _ROLES_ROOT   = {RolEnum.root}
    _ROLES_MASTER = {RolEnum.root, RolEnum.master, RolEnum.administrador}
    _ROLES_DOCENTE = {
        RolEnum.docente, RolEnum.profesor,
        RolEnum.profesor_directivo,
    }
    _ROLES_JEFE = {
        RolEnum.jefe_area, RolEnum.jefe_departamento,
    }
    _ROLES_ESTUDIANTE = {RolEnum.estudiante, RolEnum.alumno}

    @property
    def es_root(self) -> bool:
        return self.rol == RolEnum.root

    @property
    def es_master(self) -> bool:
        """Master y root (root tiene todo lo de master)."""
        return self.rol in self._ROLES_MASTER

    @property
    def es_docente(self) -> bool:
        return self.rol in self._ROLES_DOCENTE

    @property
    def es_jefe(self) -> bool:
        return self.rol in self._ROLES_JEFE

    @property
    def es_estudiante(self) -> bool:
        return self.rol in self._ROLES_ESTUDIANTE

    @property
    def es_staff(self) -> bool:
        """Cualquier rol excepto estudiante/alumno."""
        return self.rol not in self._ROLES_ESTUDIANTE

    # legacy
    @property
    def es_profesor(self) -> bool:
        return self.es_docente

    @property
    def nombre_completo(self) -> str:
        if self.apellido:
            return f"{self.nombre} {self.apellido}"
        return self.nombre

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} email={self.email} rol={self.rol}>"
