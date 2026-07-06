"""
SQLAlchemy models — reflejan las tablas gestionadas por Django (backend/).
Solo se usan para lectura/actualización del campo embedding.
No se usa Alembic: las migraciones siguen siendo responsabilidad de Django.
"""

from sqlalchemy import Column, Numeric, String, Text

from pgvector.sqlalchemy import Vector

from database import Base


class ProductoDB(Base):
    """
    Refleja la tabla 'productos' creada por Django.
    'embedding' es la columna añadida por la migración 0002_add_embedding.
    """

    __tablename__ = "productos"
    __table_args__ = {"extend_existing": True}

    codigo = Column(String(50), primary_key=True)
    nombre = Column(String(255), nullable=False)
    caracteristicas = Column(Text, nullable=True)
    precio_base = Column(Numeric(18, 2), nullable=False)
    moneda_base = Column(String(3), default="COP")
    empresa_id = Column(String(20), nullable=False)  # FK a empresas.nit
    embedding = Column(Vector(1536), nullable=True)
