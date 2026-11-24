"""Lectura del dataset. No acepta SQL del cliente."""

from datetime import date

from fastapi import APIRouter, HTTPException, Query, Request

from app.esquemas import Direccion, FiltroOrden, Granularidad, fechas_validas
from app.limite import limitar
from app.repositorio import (
    categorias,
    por_categoria,
    por_periodo,
    por_region,
    producto,
    productos,
    resumen,
    tienda,
    tiendas,
    venta,
    ventas,
    muestra,
)
from app.seguridad import leer_token

router = APIRouter(prefix="/api/v4", tags=["Datos"])


def _sesion(request: Request) -> str:
    datos = leer_token(request)
    limitar(f"api:{datos['jti']}", 120, 60, reintento=5)
    return datos["jti"]


@router.get("/productos")
def listar_productos(
    request: Request,
    categoria: str | None = Query(default=None, max_length=40),
    q: str | None = Query(default=None, max_length=40),
    page: int = Query(default=1, ge=1, le=10000),
    page_size: int = Query(default=20, ge=1, le=100),
):
    _sesion(request)
    return productos(categoria, q, page, page_size)


@router.get("/productos/{id_producto}")
def uno_producto(id_producto: int, request: Request):
    _sesion(request)
    fila = producto(id_producto)
    if fila is None:
        raise HTTPException(status_code=404, detail="El producto no existe.")
    return fila


@router.get("/categorias")
def listar_categorias(request: Request):
    _sesion(request)
    return categorias()


@router.get("/tiendas")
def listar_tiendas(
    request: Request,
    region: str | None = Query(default=None, max_length=40),
    page: int = Query(default=1, ge=1, le=1000),
    page_size: int = Query(default=20, ge=1, le=100),
):
    _sesion(request)
    return tiendas(region, page, page_size)


@router.get("/tiendas/{id_tienda}")
def una_tienda(id_tienda: int, request: Request):
    _sesion(request)
    fila = tienda(id_tienda)
    if fila is None:
        raise HTTPException(status_code=404, detail="La tienda no existe.")
    return fila


@router.get("/ventas/muestra")
def extraccion(request: Request, limite: int = Query(default=200, ge=100, le=300)):
    _sesion(request)
    return muestra(limite)


@router.get("/ventas")
def listar_ventas(
    request: Request,
    region: str | None = Query(default=None, max_length=40),
    categoria: str | None = Query(default=None, max_length=40),
    canal: str | None = Query(default=None, max_length=20),
    metodo_pago: str | None = Query(default=None, max_length=20),
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    id_producto: int | None = Query(default=None, ge=1),
    id_tienda: int | None = Query(default=None, ge=1),
    orden: FiltroOrden = "id_transaccion",
    direccion: Direccion = "asc",
    page: int = Query(default=1, ge=1, le=10000),
    page_size: int = Query(default=20, ge=1, le=100),
):
    _sesion(request)
    fechas_validas(fecha_desde, fecha_hasta)
    return ventas(
        {
            "region": region,
            "categoria": categoria,
            "canal": canal,
            "metodo_pago": metodo_pago,
            "fecha_desde": fecha_desde,
            "fecha_hasta": fecha_hasta,
            "id_producto": id_producto,
            "id_tienda": id_tienda,
        },
        orden,
        direccion,
        page,
        page_size,
    )


@router.get("/ventas/{id_transaccion}")
def una_venta(id_transaccion: int, request: Request):
    _sesion(request)
    fila = venta(id_transaccion)
    if fila is None:
        raise HTTPException(status_code=404, detail="La transaccion no existe.")
    return fila


@router.get("/indicadores/resumen")
def indicador_resumen(
    request: Request,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
):
    _sesion(request)
    fechas_validas(fecha_desde, fecha_hasta)
    return resumen(fecha_desde, fecha_hasta)


@router.get("/indicadores/ventas-por-categoria")
def indicador_categoria(request: Request):
    _sesion(request)
    return por_categoria()


@router.get("/indicadores/ventas-por-region")
def indicador_region(request: Request):
    _sesion(request)
    return por_region()


@router.get("/indicadores/ventas-por-periodo")
def indicador_periodo(request: Request, granularidad: Granularidad = "mes"):
    _sesion(request)
    return por_periodo(granularidad)
