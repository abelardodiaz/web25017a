# app/routes/cat_routes.py
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from app.models import SyscomCredential, Marca, Categoria, Producto, ProductoImagen, HistorialCambios, User
from app import db
import requests
from datetime import datetime
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Constante base para Syscom
BASE_URL = "https://developers.syscom.mx/api/v1"

catalogo_bp = Blueprint('catalogo', __name__, url_prefix='/catalogo')

@catalogo_bp.route('/mantenimiento')
@login_required
def mantenimiento():
    if not current_user.is_admin:
        flash("Acceso denegado: solo administradores.", "warning")
        return redirect(url_for('main.index'))
    
    # Obtener parámetros de búsqueda
    search_term = request.args.get('search', '')
    marca_id = request.args.get('marca', type=int)
    categoria_id = request.args.get('categoria', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Productos por página
    
    # Construir la consulta base
    query = Producto.query
    
    # Aplicar filtros
    if search_term:
        query = query.filter(Producto.titulo.ilike(f"%{search_term}%"))
    if marca_id:
        query = query.filter(Producto.marca_id == marca_id)
    if categoria_id:
        query = query.join(Producto.categorias).filter(Categoria.id == categoria_id)
    
    # Paginar los resultados
    productos = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Obtener todas las marcas y categorías para los selectores
    marcas = Marca.query.all()
    categorias = Categoria.query.all()
    
    return render_template(
        'cat/cat_mantenimiento.html',
        productos=productos.items,
        pagination=productos,
        marcas=marcas,
        categorias=categorias,
        search_term=search_term,
        selected_marca=marca_id,
        selected_categoria=categoria_id
    )



@catalogo_bp.route('/sincronizar', methods=['GET', 'POST'])
@login_required
def sincronizar():
    if not current_user.is_admin:
        flash("Acceso denegado: solo administradores.", "warning")
        return redirect(url_for('main.index'))

    productos_encontrados = []
    error = None

    if request.method == 'POST':
        # Limpiar y validar IDs
        id_list = request.form.getlist('seleccion')
        clean_ids = [pid.strip() for pid in id_list if pid.strip().isdigit()]
        
        if not clean_ids:
            flash("No se seleccionaron productos válidos", "warning")
            return redirect(url_for('catalogo.sincronizar'))

        token = _get_syscom_token()
        if not token:
            flash("Token de Syscom inválido o próximo a expirar. Actualiza tus credenciales primero.", "danger")
            return redirect(url_for('catalogo.sincronizar'))

        productos_sincronizados = 0
        errores = 0

        for pid in clean_ids:
            try:
                # Convertir a entero para la API
                producto_id = int(pid)
                resp = requests.get(
                    f"{BASE_URL}/productos/{producto_id}",
                    headers={"Authorization": f"Bearer {token}"}, 
                    timeout=15
                )
                current_app.logger.debug(f"Respuesta de Syscom para ID {pid}: {resp.status_code}")
                
                if resp.status_code != 200:
                    current_app.logger.error(f"Error {resp.status_code} al obtener producto {pid}: {resp.text[:200]}")
                    errores += 1
                    continue
                
                try:
                    data = resp.json()
                except Exception as e:
                    current_app.logger.error(f"Error decodificando JSON para ID {pid}: {str(e)}")
                    errores += 1
                    continue
                    
                producto_data = data
                
                if not producto_data or 'producto_id' not in producto_data:
                    current_app.logger.warning(f"Respuesta inválida para ID {pid}: {data}")
                    errores += 1
                    continue
                
                # Convertir ID a entero
                try:
                    producto_id = int(pid)
                except ValueError:
                    current_app.logger.error(f"ID {pid} no es un número válido")
                    errores += 1
                    continue

                # *** Upsert en base local ***
                # Marca
                nombre_marca = producto_data.get("marca") or "SinMarca"
                marca_obj = Marca.query.filter_by(nombre=nombre_marca).first()
                if not marca_obj:
                    marca_obj = Marca(nombre=nombre_marca, logo_url=producto_data.get("marca_logo"))
                    db.session.add(marca_obj)

                # Categorías
                cats = []
                for cat_dict in producto_data.get("categorias", []):
                    cid = int(cat_dict.get("id", 0))
                    cat_obj = Categoria.query.get(cid)
                    if not cat_obj:
                        cat_obj = Categoria(id=cid, nombre=cat_dict.get("nombre"), nivel=cat_dict.get("nivel", 0))
                        db.session.add(cat_obj)
                    else:
                        cat_obj.nombre = cat_dict.get("nombre")
                        cat_obj.nivel = cat_dict.get("nivel", 0)
                    cats.append(cat_obj)

                db.session.flush()

                # Producto
                producto = Producto.query.get(producto_id)
                creando = False
                if not producto:
                    producto = Producto(id=producto_id)
                    creando = True
                    db.session.add(producto)

                # Actualizar campos
                producto.modelo = producto_data.get("modelo")
                producto.titulo = producto_data.get("titulo")
                producto.descripcion = producto_data.get("descripcion")
                producto.descripcion_corta = (producto.descripcion or "")[:137] + "..." \
                    if producto.descripcion and len(producto.descripcion) > 140 else (producto.descripcion or "")

                producto.total_existencia = producto_data.get("total_existencia", 0)
                producto.sat_key = producto_data.get("sat_key")
                producto.img_portada = producto_data.get("img_portada")
                
                # Thumbnail
                imgs = producto_data.get("imagenes", [])
                producto.img_thumbnail = next(
                    (img.get("imagen") for img in imgs if "-LIST-" in img.get("imagen", "")),
                    None
                )

                # Precios
                precios = producto_data.get("precios", {})
                producto.precio_lista = precios.get("precio_lista")
                # Tomamos el precio con descuento de Syscom como nuestro precio
                # especial en la base de datos
                producto.precio_especial = precios.get("precio_descuento")

                # Recalcular precio público si no fue editado manualmente
                if not producto.precio_editado:
                    if producto.precio_lista is not None and producto.margen is not None:
                        producto.precio_publico = producto.precio_lista * (1 + (producto.margen or 0) / 100)
                    if producto.precio_publico and producto.descuento:
                        producto.precio_publico = producto.precio_publico * (1 - producto.descuento / 100)

                # Asignar marca y categorías
                producto.marca = marca_obj
                producto.categorias = cats

                # Características y recursos
                producto.caracteristicas = ";".join(producto_data.get("caracteristicas", []))
                recs = [r.get("path") for r in producto_data.get("recursos", []) if r.get("path")]
                producto.recursos = ";".join(recs)

                # Fecha de actualización
                producto.updated_at = datetime.utcnow()
                producto.visible = True

                db.session.flush()

                # Historial de cambios
                if creando:
                    cambio = HistorialCambios(
                        producto_id=producto.id,
                        usuario_id=current_user.id,
                        campo_modificado="CREACIÓN",
                        valor_anterior="–",
                        valor_nuevo=f"Producto {producto.modelo} creado",
                        timestamp=datetime.utcnow()
                    )
                    db.session.add(cambio)

                productos_sincronizados += 1
                
            except Exception as e:
                current_app.logger.exception(f"Error al sincronizar producto {pid}")
                errores += 1

        # Commit final
        try:
            db.session.commit()
            if productos_sincronizados > 0:
                flash(f"{productos_sincronizados} productos sincronizados correctamente.", "success")
            if errores > 0:
                flash(f"{errores} productos tuvieron errores durante la sincronización.", "warning")
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception("Error al hacer commit de la sincronización")
            flash("Error al guardar los cambios en la base de datos.", "danger")

        return redirect(url_for('catalogo.sincronizar'))

    # Manejar GET: Búsqueda
    token = _get_syscom_token()
    if not token:
        error = "Token de Syscom inválido o próximo a expirar. Actualiza tus credenciales."
    else:
        search_term = request.args.get('searchTerm', '')
        search_ids = request.args.get('searchIds', '')
        limit = request.args.get('resultLimit', 20, type=int)

        # Si hay IDs específicos, priorizamos esa búsqueda
        if search_ids:
            id_list = [pid.strip() for pid in search_ids.split(',') if pid.strip()]
            for pid in id_list[:limit]:
                try:
                    resp = requests.get(
                        f"{BASE_URL}/productos/{pid}",
                        headers={"Authorization": f"Bearer {token}"}, 
                        timeout=15
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data and 'producto_id' in data:
                            productos_encontrados.append({
                                "id": data.get("producto_id"),
                                "modelo": data.get("modelo"),
                                "titulo": data.get("titulo"),
                                "marca": data.get("marca"),
                                "categorias": [c.get("nombre") for c in data.get("categorias", [])],
                                "existencia": data.get("total_existencia"),
                                "imagen": data.get("img_portada") or next(
                                    (img.get("imagen") for img in data.get("imagenes", []) 
                                    if "-LIST-" in img.get("imagen", "")), None
                                )
                            })
                except Exception as e:
                    current_app.logger.error(f"Error al buscar producto {pid}: {str(e)}")

        # Si hay término de búsqueda, usar la API de búsqueda con POST
         # BÚSQUEDA POR TÉRMINO (parte corregida)
        # BÚSQUEDA POR TÉRMINO - USANDO EL MÉTODO COMPROBADO
        elif search_term:
            try:
                # Parámetros como en el script exitoso
                params = {
                    'busqueda': search_term,
                    'pagina': 1,
                    'por_pagina': limit
                }
                
                # Usar GET con parámetros en la URL
                resp = requests.get(
                    f"{BASE_URL}/productos",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
                    },
                    params=params,
                    timeout=15
                )
                
                current_app.logger.debug(f"Búsqueda Syscom: {resp.status_code}, URL: {resp.url}")
                
                if resp.status_code == 200:
                    data = resp.json()
                    if 'productos' in data:
                        for prod in data['productos'][:limit]:
                            productos_encontrados.append({
                                "id": prod.get("producto_id"),
                                "modelo": prod.get("modelo"),
                                "titulo": prod.get("titulo"),
                                "marca": prod.get("marca"),
                                "categorias": [c.get("nombre") for c in prod.get("categorias", [])],
                                "existencia": prod.get("total_existencia"),
                                "imagen": prod.get("img_portada") or next(
                                    (img.get("imagen") for img in prod.get("imagenes", []) 
                                    if "-LIST-" in img.get("imagen", "")), None
                                )
                            })
                    else:
                        error = "Formato de respuesta inesperado de Syscom"
                        current_app.logger.error(f"Estructura respuesta inválida: {data.keys()}")
                else:
                    error = f"Error en API Syscom: {resp.status_code} - {resp.text}"
                    current_app.logger.error(f"Error en búsqueda: {resp.text}")
                
            except Exception as e:
                current_app.logger.exception("Error en búsqueda por término")
                error = f"Error de conexión: {str(e)}"

                

    return render_template(
        'cat/cat_sinc.html',
        productos=productos_encontrados,
        error=error
    )


def _get_syscom_token():
    """
    Versión simplificada como en tu prueba exitosa
    """
    cred = SyscomCredential.query.order_by(SyscomCredential.updated_at.desc()).first()
    if cred and cred.token:
        # Verificación mínima de expiración
        if cred.expires_at and cred.expires_at > datetime.utcnow():
            return cred.token
    return None


@catalogo_bp.route('/alta')
def alta():
    return render_template('cat/cat_alta.html')