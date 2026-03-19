from flask import Flask, jsonify, request
from conexion import ConexionDB
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.json.sort_keys = False


@app.after_request
def aplicar_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
    return response


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Gedeon1990'
app.config['MYSQL_DB'] = 'tecno_city_zone'

try:
    db = ConexionDB(
        app.config['MYSQL_HOST'],
        app.config['MYSQL_USER'],
        app.config['MYSQL_PASSWORD'],
        app.config['MYSQL_DB']
    )
except Exception:
    db = None


HAS_USUARIO_COLUMN = False
if db is not None:
    try:
        _cursor = db.obtener_cursor()
        _cursor.execute('SHOW COLUMNS FROM usuarios')
        _cols = [fila[0] for fila in _cursor.fetchall()]
        HAS_USUARIO_COLUMN = 'usuario' in _cols

        _cursor.execute('SHOW COLUMNS FROM productos')
        _producto_cols = [fila[0] for fila in _cursor.fetchall()]

        if 'categoria' not in _producto_cols:
            _cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(80) NOT NULL DEFAULT 'Sin categoria' AFTER modelo")
            db.conexion.commit()
            _producto_cols.append('categoria')

    except Exception:
        HAS_USUARIO_COLUMN = False


PRODUCTOS_SELECT_FIELDS = 'id, nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo'


def leer_payload():
    data = request.get_json(silent=True)
    if not data:
        data = request.form
    return data


def sincronizar_categorias_productos():
    if db is None:
        return

    cursor = db.obtener_cursor()
    cursor.execute(
        """
        UPDATE productos
        SET categoria = CASE
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%micro sd%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%microsd%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%memoria usb%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%disco duro%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%disco externo%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%ssd%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%hdd%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%almacenamiento%'
                    THEN 'Almacenamiento'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%audifono%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%audífono%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%audio%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%speaker%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%parlante%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%microfono%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%micrófono%'
                    THEN 'Sonido'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%teclado%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%mouse%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%laptop%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%computadora%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%tablet%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%monitor%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%webcam%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%impresora%'
                    THEN 'Computo'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%router%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%wifi%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%wi-fi%'
                    THEN 'Redes'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%smartwatch%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%reloj%'
                    THEN 'Wearables'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%televisor%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%smart tv%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '% tv%'
                    THEN 'Televisores'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%gamer%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%gaming%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%control%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%xbox%'
                    THEN 'Gaming'
            WHEN LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%silla%'
                OR LOWER(CONCAT(COALESCE(nombre, ''), ' ', COALESCE(descripcion, ''), ' ', COALESCE(modelo, ''), ' ', COALESCE(marca, ''))) LIKE '%accesorio%'
                    THEN 'Accesorios'
            ELSE 'Otros'
        END
        WHERE categoria IS NULL OR TRIM(categoria) = '' OR categoria = 'Sin categoria'
        """
    )
    db.conexion.commit()


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
        'activo': bool(fila[13]),
    }


@app.route('/api/productos', methods=['GET'])
def listar_productos():
    if db is None:
        return jsonify({'exito': False, 'mensaje': 'No hay conexion a MySQL en este momento.', 'datos': []}), 503

    sincronizar_categorias_productos()

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

    sincronizar_categorias_productos()

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
    activo = 1 if bool(data.get('activo', True)) else 0

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
    activo = 1 if bool(data.get('activo', True)) else 0

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
    if HAS_USUARIO_COLUMN:
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

    if password:
        password_hash = generate_password_hash(password)
        cursor.execute(
            'UPDATE usuarios SET username=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s, password=%s WHERE id=%s',
            (nombre, telefono, nombre, correo, edad, rol, password_hash, usuario_id)
        )
    else:
        cursor.execute(
            'UPDATE usuarios SET username=%s, telefono=%s, nombre=%s, correo=%s, edad=%s, rol=%s WHERE id=%s',
            (nombre, telefono, nombre, correo, edad, rol, usuario_id)
        )

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

    if HAS_USUARIO_COLUMN:
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


if __name__ == '__main__':
    app.run(debug=True)
