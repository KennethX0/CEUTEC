from pathlib import Path
from flask import Flask, jsonify, request, render_template
try:
    from .conexion import ConexionDB
except ImportError:
    from conexion import ConexionDB
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import random
import os

BASE_DIR = Path(__file__).resolve().parent
LEGACY_FRONTEND_DIR = BASE_DIR / 'Frontend'

if (LEGACY_FRONTEND_DIR / 'templates').exists():
    TEMPLATE_DIR = LEGACY_FRONTEND_DIR / 'templates'
elif (BASE_DIR / 'templates').exists():
    TEMPLATE_DIR = BASE_DIR / 'templates'
else:
    TEMPLATE_DIR = BASE_DIR

if (LEGACY_FRONTEND_DIR / 'static').exists():
    STATIC_DIR = LEGACY_FRONTEND_DIR / 'static'
elif (BASE_DIR / 'static').exists():
    STATIC_DIR = BASE_DIR / 'static'
else:
    STATIC_DIR = BASE_DIR

app = Flask(
    __name__,
    template_folder=str(TEMPLATE_DIR),
    static_folder=str(STATIC_DIR),
    static_url_path='/static',
)
app.json.sort_keys = False


@app.after_request
def agregar_headers_cors(respuesta):
    origen = request.headers.get('Origin')
    respuesta.headers['Access-Control-Allow-Origin'] = origen if origen else '*'
    respuesta.headers['Vary'] = 'Origin'
    respuesta.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    respuesta.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return respuesta


app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'Gedeon1990')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'tecno_city_zone')

try:
    db = ConexionDB(
        app.config['MYSQL_HOST'],
        app.config['MYSQL_USER'],
        app.config['MYSQL_PASSWORD'],
        app.config['MYSQL_DB']
    )
except Exception:
    db = None


if db is not None:
    try:
        _cursor = db.obtener_cursor()
        _cursor.execute('SHOW COLUMNS FROM productos')
        _producto_cols = [fila[0] for fila in _cursor.fetchall()]

        # Se comenta porque la columna 'categoria' ya se define en el CREATE TABLE
        # del database_script.sql. Tener un ALTER TABLE al inicio del app.py es
        # redundante y genera confusion sobre la estructura de la base de datos.
        #if 'categoria' not in _producto_cols:
        #    _cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(80) NOT NULL DEFAULT 'Sin categoria' AFTER modelo")
        #    db.conexion.commit()
        #    _producto_cols.append('categoria')

    except Exception:
        pass


USUARIOS_TIENE_CAMPO_USUARIO = False
if db is not None:
    try:
        _cursor = db.obtener_cursor()
        _cursor.execute('SHOW COLUMNS FROM usuarios')
        _usuario_cols = [fila[0] for fila in _cursor.fetchall()]
        USUARIOS_TIENE_CAMPO_USUARIO = 'usuario' in _usuario_cols
    except Exception:
        USUARIOS_TIENE_CAMPO_USUARIO = False


PRODUCTOS_SELECT_FIELDS = 'id, nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo'


def valor_a_bool(valor, por_defecto=True):
    """Convierte diversos tipos de valores a booleano de forma segura."""
    if valor is None:
        return por_defecto

    if isinstance(valor, bool):
        return valor

    if isinstance(valor, (int, float)):
        return int(valor) != 0

    texto = str(valor).strip().lower()
    if texto in ('1', 'true', 't', 'si', 'sí', 'yes', 'y', 'on'):
        return True
    if texto in ('0', 'false', 'f', 'no', 'n', 'off', ''):
        return False

    return por_defecto


def leer_payload():
    data = request.get_json(silent=True)
    if not data:
        data = request.form
    return data


def generar_numero_factura():
    marca_tiempo = datetime.now().strftime('%Y%m%d%H%M%S')
    aleatorio = random.randint(100, 999)
    return f'FAC-{marca_tiempo}-{aleatorio}'


def producto_a_dict(fila):
    return {
        'id': fila[0],
        'nombre': fila[1],
        'marca': fila[2],
        'modelo': fila[3],
        'categoria': fila[4],
        'precio': float(fila[5]),
        'descripcion': fila[6],
        'tamano': fila[7],
        'peso': fila[8],
        'color': fila[9],
        'conexion': fila[10],
        'garantia': fila[11],
        'imagen': fila[12],
        'activo': valor_a_bool(fila[13], por_defecto=False),
    }


@app.route('/api/productos', methods=['GET'])
def listar_productos():
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.', 'datos': []}), 503

    activos = request.args.get('activos')
    activos = str(activos).strip().lower() if activos is not None else ''
    mostrar_todos = activos in ('all', 'todos', 'false', '0', 'no')

    cursor = db.obtener_cursor()
    if mostrar_todos:
        cursor.execute(
            f'SELECT {PRODUCTOS_SELECT_FIELDS} FROM productos ORDER BY id DESC'
        )
    else:
        cursor.execute(
            f'SELECT {PRODUCTOS_SELECT_FIELDS} FROM productos WHERE activo=1 ORDER BY id DESC'
        )

    filas = cursor.fetchall()
    datos = [producto_a_dict(fila) for fila in filas]
    return jsonify({'total': len(datos), 'datos': datos, 'exito': True}), 200


@app.route('/api/productos/<int:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute(
        f'SELECT {PRODUCTOS_SELECT_FIELDS} FROM productos WHERE id=%s',
        (id_producto,)
    )
    fila = cursor.fetchone()

    if not fila:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado.'}), 404

    return jsonify({'exito': True, 'datos': producto_a_dict(fila)}), 200


@app.route('/api/productos', methods=['POST'])
def crear_producto():
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = request.get_json(silent=True) or {}

    nombre = str(data.get('nombre', '')).strip()
    marca = str(data.get('marca', '')).strip() or None
    modelo = str(data.get('modelo', '')).strip() or None
    categoria = str(data.get('categoria', '')).strip() or 'Sin categoria'
    descripcion = str(data.get('descripcion', '')).strip()
    tamano = str(data.get('tamano', '')).strip() or None
    peso = str(data.get('peso', '')).strip() or None
    color = str(data.get('color', '')).strip() or None
    conexion = str(data.get('conexion', '')).strip() or None
    garantia = str(data.get('garantia', '')).strip() or None
    imagen = str(data.get('imagen', '')).strip() or None
    activo = 1 if valor_a_bool(data.get('activo'), por_defecto=True) else 0

    try:
        precio = float(data.get('precio', 0))
    except (TypeError, ValueError):
        precio = 0

    if not nombre or not descripcion or precio <= 0:
        return jsonify({'exito': False, 'mensaje': 'Completa nombre, precio y descripcion correctamente.'}), 400

    cursor = db.obtener_cursor()
    cursor.execute(
        'INSERT INTO productos (nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo)
    )
    db.conexion.commit()

    return jsonify({'exito': True, 'mensaje': 'Producto creado correctamente.'}), 201


@app.route('/api/productos/<int:id_producto>', methods=['PUT'])
def actualizar_producto(id_producto):
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = request.get_json(silent=True) or {}

    nombre = str(data.get('nombre', '')).strip()
    marca = str(data.get('marca', '')).strip() or None
    modelo = str(data.get('modelo', '')).strip() or None
    categoria = str(data.get('categoria', '')).strip() or 'Sin categoria'
    descripcion = str(data.get('descripcion', '')).strip()
    tamano = str(data.get('tamano', '')).strip() or None
    peso = str(data.get('peso', '')).strip() or None
    color = str(data.get('color', '')).strip() or None
    conexion = str(data.get('conexion', '')).strip() or None
    garantia = str(data.get('garantia', '')).strip() or None
    imagen = str(data.get('imagen', '')).strip() or None
    activo = 1 if valor_a_bool(data.get('activo'), por_defecto=True) else 0

    try:
        precio = float(data.get('precio', 0))
    except (TypeError, ValueError):
        precio = 0

    if not nombre or not descripcion or precio <= 0:
        return jsonify({'exito': False, 'mensaje': 'Completa nombre, precio y descripcion correctamente.'}), 400

    cursor = db.obtener_cursor()
    cursor.execute('SELECT id FROM productos WHERE id=%s', (id_producto,))
    existe = cursor.fetchone()
    if not existe:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado.'}), 404

    cursor.execute(
        'UPDATE productos SET nombre=%s, marca=%s, modelo=%s, categoria=%s, precio=%s, descripcion=%s, tamano=%s, peso=%s, color=%s, conexion=%s, garantia=%s, imagen=%s, activo=%s WHERE id=%s',
        (nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo, id_producto)
    )
    db.conexion.commit()

    return jsonify({'exito': True, 'mensaje': 'Producto actualizado correctamente.'}), 200


@app.route('/api/productos/<int:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute('SELECT id FROM productos WHERE id=%s', (id_producto,))
    existe = cursor.fetchone()
    if not existe:
        return jsonify({'exito': False, 'mensaje': 'Producto no encontrado.'}), 404

    cursor.execute('DELETE FROM productos WHERE id=%s', (id_producto,))
    db.conexion.commit()

    return jsonify({'exito': True, 'mensaje': 'Producto eliminado correctamente.'}), 200


@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute(
        'SELECT id, telefono, nombre, correo, edad, rol FROM usuarios ORDER BY id DESC'
    )

    filas = cursor.fetchall()
    usuarios = [
        {
            'id': fila[0],
            'telefono': fila[1],
            'nombre': fila[2],
            'correo': fila[3],
            'edad': fila[4],
            'rol': fila[5],
        }
        for fila in filas
    ]

    return jsonify({'total': len(usuarios), 'usuarios': usuarios}), 200


@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = leer_payload()

    telefono = str(data.get('telefono', '')).strip()
    nombre = str(data.get('nombre', '')).strip()
    password = str(data.get('password', '')).strip()
    correo = str(data.get('correo', '')).strip()
    rol = str(data.get('rol', 'usuario')).strip().lower() or 'usuario'

    try:
        edad = int(data.get('edad', 0))
    except (TypeError, ValueError):
        edad = 0

    if rol not in ('admin', 'usuario'):
        return jsonify({'mensaje': 'Rol invalido. Usa admin o usuario.'}), 400

    if not telefono or not nombre or not password or not correo or edad < 1:
        return jsonify({'mensaje': 'Completa todos los campos requeridos.'}), 400

    if '@' not in correo:
        return jsonify({'mensaje': 'Correo invalido.'}), 400

    cursor = db.obtener_cursor()

    cursor.execute('SELECT id FROM usuarios WHERE username=%s', (nombre,))
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese nombre de usuario ya existe.'}), 409

    cursor.execute('SELECT id FROM usuarios WHERE telefono=%s', (telefono,))
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese telefono ya esta registrado.'}), 409

    cursor.execute('SELECT id FROM usuarios WHERE correo=%s', (correo,))
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese correo ya esta registrado.'}), 409

    password_hash = generate_password_hash(password)

    try:
        if USUARIOS_TIENE_CAMPO_USUARIO:
            cursor.execute(
                'INSERT INTO usuarios (username, usuario, telefono, password, rol, nombre, correo, edad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                (nombre, nombre, telefono, password_hash, rol, nombre, correo, edad)
            )
        else:
            cursor.execute(
                'INSERT INTO usuarios (username, telefono, password, rol, nombre, correo, edad) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                (nombre, telefono, password_hash, rol, nombre, correo, edad)
            )
        db.conexion.commit()
    except Exception:
        db.conexion.rollback()
        return jsonify({'mensaje': 'No se pudo crear el usuario por un problema en la base de datos.'}), 500

    return jsonify({'mensaje': 'Usuario creado correctamente.'}), 201


@app.route('/usuarios/<int:usuario_id>', methods=['GET'])
def obtener_usuario(usuario_id):
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute(
        'SELECT id, telefono, nombre, correo, edad, rol FROM usuarios WHERE id=%s',
        (usuario_id,)
    )
    fila = cursor.fetchone()

    if not fila:
        return jsonify({'mensaje': 'Usuario no encontrado.'}), 404

    usuario = {
        'id': fila[0],
        'telefono': fila[1],
        'nombre': fila[2],
        'correo': fila[3],
        'edad': fila[4],
        'rol': fila[5],
    }

    return jsonify(usuario), 200


@app.route('/usuarios/<int:usuario_id>', methods=['PUT'])
def actualizar_usuario(usuario_id):
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = leer_payload()

    telefono = str(data.get('telefono', '')).strip()
    nombre = str(data.get('nombre', '')).strip()
    correo = str(data.get('correo', '')).strip()
    rol = str(data.get('rol', 'usuario')).strip().lower() or 'usuario'
    password = str(data.get('password', '')).strip()

    try:
        edad = int(data.get('edad', 0))
    except (TypeError, ValueError):
        edad = 0

    if rol not in ('admin', 'usuario'):
        return jsonify({'mensaje': 'Rol invalido. Usa admin o usuario.'}), 400

    if not telefono or not nombre or not correo or edad < 1:
        return jsonify({'mensaje': 'Completa todos los campos requeridos.'}), 400

    if '@' not in correo:
        return jsonify({'mensaje': 'Correo invalido.'}), 400

    cursor = db.obtener_cursor()
    cursor.execute('SELECT id, rol FROM usuarios WHERE id=%s', (usuario_id,))
    actual = cursor.fetchone()

    if not actual:
        return jsonify({'mensaje': 'Usuario no encontrado.'}), 404

    cursor.execute(
        'SELECT id FROM usuarios WHERE username=%s AND id<>%s',
        (nombre, usuario_id)
    )
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese nombre de usuario ya existe.'}), 409

    cursor.execute(
        'SELECT id FROM usuarios WHERE telefono=%s AND id<>%s',
        (telefono, usuario_id)
    )
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese telefono ya esta registrado.'}), 409

    cursor.execute(
        'SELECT id FROM usuarios WHERE correo=%s AND id<>%s',
        (correo, usuario_id)
    )
    if cursor.fetchone():
        return jsonify({'mensaje': 'Ese correo ya esta registrado.'}), 409

    try:
        if password:
            password_hash = generate_password_hash(password)
            if USUARIOS_TIENE_CAMPO_USUARIO:
                cursor.execute(
                    'UPDATE usuarios SET username=%s, usuario=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s, password=%s WHERE id=%s',
                    (nombre, nombre, telefono, nombre, correo, edad, rol, password_hash, usuario_id)
                )
            else:
                cursor.execute(
                    'UPDATE usuarios SET username=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s, password=%s WHERE id=%s',
                    (nombre, telefono, nombre, correo, edad, rol, password_hash, usuario_id)
                )
        else:
            if USUARIOS_TIENE_CAMPO_USUARIO:
                cursor.execute(
                    'UPDATE usuarios SET username=%s, usuario=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s WHERE id=%s',
                    (nombre, nombre, telefono, nombre, correo, edad, rol, usuario_id)
                )
            else:
                cursor.execute(
                    'UPDATE usuarios SET username=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s WHERE id=%s',
                    (nombre, telefono, nombre, correo, edad, rol, usuario_id)
                )
    except Exception:
        db.conexion.rollback()
        return jsonify({'mensaje': 'No se pudo actualizar el usuario por un problema en la base de datos.'}), 500

    db.conexion.commit()
    return jsonify({'mensaje': 'Usuario actualizado correctamente.'}), 200


@app.route('/usuarios/<int:usuario_id>', methods=['DELETE'])
def eliminar_usuario(usuario_id):
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute('SELECT id, rol FROM usuarios WHERE id=%s', (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({'mensaje': 'Usuario no encontrado.'}), 404

    if str(usuario[1]).lower() == 'admin':
        return jsonify({'mensaje': 'No se puede eliminar el usuario admin.'}), 403

    cursor.execute('DELETE FROM usuarios WHERE id=%s', (usuario_id,))
    db.conexion.commit()

    return jsonify({'mensaje': 'Usuario eliminado correctamente.'}), 200


@app.route('/register', methods=['POST'])
def register():
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = request.get_json(silent=True)
    if not data:
        data = request.form

    telefono = str(data.get('telefono', '')).strip()
    nombre = str(data.get('nombre', '')).strip()
    password = str(data.get('password', '')).strip()
    correo = str(data.get('correo', '')).strip()

    try:
        edad = int(data.get('edad', 0))
    except (TypeError, ValueError):
        edad = 0

    if not telefono or not nombre or not password or not correo or edad < 1:
        return jsonify({'mensaje': 'Completa todos los campos requeridos.'}), 400

    if '@' not in correo:
        return jsonify({'mensaje': 'Correo invalido.'}), 400

    username = nombre

    cursor = db.obtener_cursor()

    cursor.execute('SELECT id FROM usuarios WHERE username=%s', (username,))
    existente = cursor.fetchone()
    if existente:
        return jsonify({'mensaje': 'Ese nombre ya esta registrado.'}), 409

    cursor.execute('SELECT id FROM usuarios WHERE telefono=%s', (telefono,))
    existe_telefono = cursor.fetchone()
    if existe_telefono:
        return jsonify({'mensaje': 'Ese telefono ya esta registrado.'}), 409

    cursor.execute('SELECT id FROM usuarios WHERE correo=%s', (correo,))
    existe_correo = cursor.fetchone()
    if existe_correo:
        return jsonify({'mensaje': 'Ese correo ya esta registrado.'}), 409

    password_hash = generate_password_hash(password)

    try:
        if USUARIOS_TIENE_CAMPO_USUARIO:
            cursor.execute(
                'INSERT INTO usuarios (username, usuario, telefono, password, rol, nombre, correo, edad) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',
                (username, username, telefono, password_hash, 'usuario', nombre, correo, edad)
            )
        else:
            cursor.execute(
                'INSERT INTO usuarios (username, telefono, password, rol, nombre, correo, edad) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                (username, telefono, password_hash, 'usuario', nombre, correo, edad)
            )

        db.conexion.commit()
    except Exception:
        db.conexion.rollback()
        return jsonify({'mensaje': 'No se pudo registrar el usuario por un problema en la base de datos.'}), 500

    return jsonify({'mensaje': 'Usuario registrado correctamente'}), 201


@app.route('/login', methods=['POST'])
def login():
    if db is None:
        return jsonify({'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = request.get_json(silent=True)
    if not data:
        data = request.form

    login_value = str(data.get('username', '')).strip()
    password = str(data.get('password', '')).strip()

    if not login_value or not password:
        return jsonify({'mensaje': 'Nombre, telefono o correo y contrasena son requeridos.'}), 400

    cursor = db.obtener_cursor()

    cursor.execute(
        'SELECT username,password,rol,correo,nombre,telefono FROM usuarios WHERE username=%s OR correo=%s OR telefono=%s',
        (login_value, login_value, login_value)
    )

    usuario = cursor.fetchone()

    if not usuario:
        return jsonify({'mensaje': 'Usuario no existe, debe registrarse'}), 404

    password_db = str(usuario[1])
    es_hash = password_db.startswith('pbkdf2:') or password_db.startswith('scrypt:')
    password_ok = check_password_hash(password_db, password) if es_hash else password_db == password

    if not password_ok:
        return jsonify({'mensaje': 'Contrasena incorrecta'}), 401

    if usuario[2] == 'admin':
        return jsonify({
            'mensaje': 'Bienvenido Admin',
            'rol': 'admin',
            'telefono': usuario[5],
            'correo': usuario[3],
            'nombre': usuario[4],
        })

    return jsonify({
        'mensaje': 'Bienvenido Usuario',
        'rol': 'usuario',
        'telefono': usuario[5],
        'correo': usuario[3],
        'nombre': usuario[4],
    })


@app.route('/api/facturas', methods=['POST'])
def crear_factura():
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    data = request.get_json(silent=True) or {}

    nombre = str(data.get('nombre', '')).strip()
    direccion = str(data.get('direccion', '')).strip()
    telefono = str(data.get('telefono', '')).strip()
    metodo_pago = str(data.get('metodo_pago', '')).strip().lower()
    usuario_nombre = str(data.get('usuario', '')).strip() or None
    items = data.get('items', [])

    if not nombre or not direccion or not telefono:
        return jsonify({'exito': False, 'mensaje': 'Nombre, direccion y telefono son obligatorios.'}), 400

    if metodo_pago not in ('paypal', 'tarjeta'):
        return jsonify({'exito': False, 'mensaje': 'Metodo de pago invalido. Usa paypal o tarjeta.'}), 400

    if not isinstance(items, list) or not items:
        return jsonify({'exito': False, 'mensaje': 'La compra no contiene productos.'}), 400

    items_limpios = []
    subtotal = 0.0

    for item in items:
        try:
            producto_id = int(item.get('id', 0)) if item.get('id') is not None else None
        except (TypeError, ValueError):
            producto_id = None

        nombre_producto = str(item.get('nombre', '')).strip()

        try:
            precio = float(item.get('precio', 0))
        except (TypeError, ValueError):
            precio = 0.0

        try:
            cantidad = int(item.get('cantidad', 0))
        except (TypeError, ValueError):
            cantidad = 0

        if not nombre_producto or precio <= 0 or cantidad <= 0:
            return jsonify({'exito': False, 'mensaje': 'Hay productos invalidos en la compra.'}), 400

        subtotal_linea = round(precio * cantidad, 2)
        subtotal += subtotal_linea

        items_limpios.append({
            'producto_id': producto_id,
            'nombre': nombre_producto,
            'precio': round(precio, 2),
            'cantidad': cantidad,
            'subtotal': subtotal_linea,
        })

    subtotal = round(subtotal, 2)
    envio = 10.00
    total = round(subtotal + envio, 2)
    numero_factura = generar_numero_factura()

    cursor = db.obtener_cursor()

    try:
        cursor.execute(
            'INSERT INTO facturas (numero_factura, cliente_nombre, direccion, telefono, metodo_pago, usuario_nombre, subtotal, envio, total) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            (numero_factura, nombre, direccion, telefono, metodo_pago, usuario_nombre, subtotal, envio, total)
        )
        factura_id = cursor.lastrowid

        for item in items_limpios:
            cursor.execute(
                'INSERT INTO factura_detalles (factura_id, producto_id, producto_nombre, precio_unitario, cantidad, subtotal) VALUES (%s,%s,%s,%s,%s,%s)',
                (factura_id, item['producto_id'], item['nombre'], item['precio'], item['cantidad'], item['subtotal'])
            )

        db.conexion.commit()
    except Exception:
        db.conexion.rollback()
        return jsonify({'exito': False, 'mensaje': 'No se pudo registrar la factura.'}), 500

    return jsonify({
        'exito': True,
        'mensaje': 'Compra confirmada y factura guardada.',
        'factura': {
            'id': factura_id,
            'numero_factura': numero_factura,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nombre': nombre,
            'direccion': direccion,
            'telefono': telefono,
            'metodo_pago': metodo_pago,
            'subtotal': subtotal,
            'envio': envio,
            'total': total,
            'items': items_limpios,
        }
    }), 201


@app.route('/api/facturas', methods=['GET'])
def listar_facturas():
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.', 'datos': []}), 503

    cursor = db.obtener_cursor()
    cursor.execute(
        'SELECT id, numero_factura, cliente_nombre, direccion, telefono, metodo_pago, usuario_nombre, subtotal, envio, total, fecha FROM facturas ORDER BY id DESC'
    )
    filas = cursor.fetchall()

    datos = [
        {
            'id': fila[0],
            'numero_factura': fila[1],
            'cliente_nombre': fila[2],
            'direccion': fila[3],
            'telefono': fila[4],
            'metodo_pago': fila[5],
            'usuario_nombre': fila[6],
            'subtotal': float(fila[7]),
            'envio': float(fila[8]),
            'total': float(fila[9]),
            'fecha': fila[10].strftime('%Y-%m-%d %H:%M:%S') if fila[10] else None,
        }
        for fila in filas
    ]

    return jsonify({'exito': True, 'total': len(datos), 'datos': datos}), 200


@app.route('/api/facturas/<int:factura_id>', methods=['DELETE'])
def eliminar_factura(factura_id):
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.'}), 503

    cursor = db.obtener_cursor()
    cursor.execute('SELECT id FROM facturas WHERE id=%s', (factura_id,))
    factura = cursor.fetchone()

    if not factura:
        return jsonify({'exito': False, 'mensaje': 'Factura no encontrada.'}), 404

    try:
        cursor.execute('DELETE FROM facturas WHERE id=%s', (factura_id,))
        db.conexion.commit()
    except Exception:
        db.conexion.rollback()
        return jsonify({'exito': False, 'mensaje': 'No se pudo eliminar la factura.'}), 500

    return jsonify({'exito': True, 'mensaje': 'Factura eliminada correctamente.'}), 200


@app.route('/')
def vista_inicio():
    return render_template('index.html')


@app.route('/<pagina>.html')
def vista_pagina(pagina):
    return render_template(f'{pagina}.html')


if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(host=host, port=port, debug=debug)
