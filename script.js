var pagina = document.body.dataset.page;

function resolverBackendOrigin() {
	var configurado = String(localStorage.getItem("backendOrigin") || "").trim();
	if (configurado) return configurado.replace(/\/$/, "");

	if (window.location.protocol === "file:") {
		return "http://127.0.0.1:5000";
	}

	if (window.location.port === "5500" || window.location.port === "5501") {
		return window.location.protocol + "//" + window.location.hostname + ":5000";
	}

	return window.location.origin;
}

var ORIGIN = resolverBackendOrigin();
var API = ORIGIN + "/api";
var AUTH_API = ORIGIN;
var productosCatalogo = [];
var categoriaActiva = "all";
var ordenCatalogo = "az";
var presupuestoCatalogo = "";
var adminEstadoFiltro = "all";
var adminCategoriaFiltro = "all";
var adminOrdenNombre = "az";

function obtenerSesion() {
	var datos = sessionStorage.getItem("authUser");
	if (datos) {
		return JSON.parse(datos);
	}
	return null;
}

function guardarSesion(usuario) {
	sessionStorage.setItem("authUser", JSON.stringify(usuario));
}

function cerrarSesion() {
	sessionStorage.removeItem("authUser");
}

function formatoPrecio(cantidad) {
	return "$ " + Number(cantidad).toFixed(2);
}

function pasaLuhn(numeroTarjeta) {
	var suma = 0;
	var duplicar = false;

	for (var i = numeroTarjeta.length - 1; i >= 0; i--) {
		var digito = Number(numeroTarjeta.charAt(i));
		if (duplicar) {
			digito = digito * 2;
			if (digito > 9) digito = digito - 9;
		}
		suma += digito;
		duplicar = !duplicar;
	}

	return suma % 10 === 0;
}

function validarNumeroTarjeta(numeroTarjeta) {
	var limpio = String(numeroTarjeta || "").replace(/\s+/g, "");
	if (!/^\d{13,19}$/.test(limpio)) return false;
	return pasaLuhn(limpio);
}

function validarNombreTitular(nombreTitular) {
	var valor = String(nombreTitular || "").trim();
	if (valor.length < 3) return false;
	return /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$/.test(valor);
}

function validarFechaVencimiento(fechaVencimiento) {
	var valor = String(fechaVencimiento || "").trim();
	if (!/^(0[1-9]|1[0-2])\/\d{4}$/.test(valor)) return false;

	var partes = valor.split("/");
	var mes = Number(partes[0]);
	var anio = Number(partes[1]);

	var hoy = new Date();
	var anioActual = hoy.getFullYear();
	var mesActual = hoy.getMonth() + 1;

	if (anio < anioActual) return false;
	if (anio === anioActual && mes < mesActual) return false;

	return true;
}

function mostrarErrorPago(mensaje) {
	var errorPago = document.getElementById("checkout-error");
	if (!errorPago) return;
	if (!mensaje) {
		errorPago.textContent = "";
		errorPago.hidden = true;
		return;
	}
	errorPago.textContent = mensaje;
	errorPago.hidden = false;
}

function validarCvv(cvv) {
	var valor = String(cvv || "").trim();
	return /^\d{3,4}$/.test(valor);
}

function validarCorreo(correo) {
	var valor = String(correo || "").trim();
	return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(valor);
}

function productoEstaActivo(producto) {
	return producto && (producto.activo === true || producto.activo === 1 || producto.activo === "1");
}

function obtenerCarrito() {
	var datos = localStorage.getItem("carrito");
	if (datos) {
		return JSON.parse(datos);
	}
	return [];
}

function guardarCarrito(carrito) {
	localStorage.setItem("carrito", JSON.stringify(carrito));
}

function cambiarCantidadCarrito(idProducto, delta) {
	var carrito = obtenerCarrito();
	for (var i = 0; i < carrito.length; i++) {
		if (Number(carrito[i].id) === Number(idProducto)) {
			var nuevaCantidad = Number(carrito[i].cantidad || 0) + Number(delta || 0);
			if (nuevaCantidad < 1) {
				nuevaCantidad = 1;
			}
			carrito[i].cantidad = nuevaCantidad;
			break;
		}
	}
	guardarCarrito(carrito);
}

function eliminarDelCarrito(idProducto) {
	var carrito = obtenerCarrito();
	var nuevoCarrito = [];
	for (var i = 0; i < carrito.length; i++) {
		if (Number(carrito[i].id) !== Number(idProducto)) {
			nuevoCarrito.push(carrito[i]);
		}
	}
	guardarCarrito(nuevoCarrito);
}

function vaciarCarrito() {
	guardarCarrito([]);
}

function requiereAdmin() {
	var sesion = obtenerSesion();
	if (!sesion || String(sesion.rol || "").toLowerCase() !== "admin") {
		alert("Debes iniciar sesion como administrador.");
		window.location.href = "login.html";
		return false;
	}
	return true;
}

function actualizarNav() {
	var navLinks = document.querySelector(".nav-links");
	if (!navLinks) return;

	var sesion = obtenerSesion();
	var loginLink = navLinks.querySelector('a[href="login.html"]');

	if (sesion && loginLink) {
		var rol = String(sesion.rol || "usuario").toLowerCase();
		var nombreSesion = sesion.nombre || sesion.usuario || "Mi cuenta";
		var logoutLink = navLinks.querySelector('[data-logout="true"]');
		var esPublica = (pagina === "index" || pagina === "detalle" || pagina === "carrito");

		if (esPublica && rol === "admin") {
			var linkAdmin = document.createElement("a");
			linkAdmin.href = "producto.html";
			linkAdmin.textContent = "Administracion";
			navLinks.insertBefore(linkAdmin, loginLink);
		}

		loginLink.textContent = nombreSesion;
		loginLink.href = rol === "admin" ? "producto.html" : "index.html";

		if (!logoutLink) {
			logoutLink = document.createElement("a");
			logoutLink.href = "#";
			logoutLink.textContent = "Cerrar sesion";
			logoutLink.dataset.logout = "true";
			navLinks.appendChild(logoutLink);
		}

		logoutLink.addEventListener("click", function(e) {
			e.preventDefault();
			cerrarSesion();
			window.location.href = "index.html";
		});
	}
}


function configurarRegistro() {
	var formulario = document.getElementById("register-form");
	if (!formulario) return;

	formulario.addEventListener("submit", async function(e) {
		e.preventDefault();

		var payload = {
			telefono: String(formulario.telefono.value || "").trim(),
			nombre: String(formulario.nombre.value || "").trim(),
			password: String(formulario.password.value || "").trim(),
			correo: String(formulario.correo.value || "").trim(),
			edad: Number(formulario.edad.value || 0)
		};

		if (!payload.telefono || !payload.nombre || !payload.password || !payload.correo || payload.edad < 1) {
			alert("Completa todos los campos requeridos.");
			return;
		}

		if (payload.correo.indexOf("@") === -1) {
			alert("Correo invalido.");
			return;
		}

		try {
			var respuesta = await fetch(AUTH_API + "/register", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify(payload)
			});

			var json = await respuesta.json();

			if (respuesta.ok) {
				alert(json.mensaje || "Usuario registrado correctamente");
				window.location.href = "login.html";
			} else {
				alert(json.mensaje || "No se pudo registrar el usuario.");
			}
		} catch (error) {
			alert("Error de conexion.");
		}
	});
}


async function mostrarCatalogo() {
	var lista = document.getElementById("product-list");
	if (!lista) return;

	lista.innerHTML = "<p>Cargando productos...</p>";

	try {
		var respuesta = await fetch(API + "/productos?activos=all");
		var json = await respuesta.json();

		if (!json.exito) {
			lista.innerHTML = "<p>Error al cargar los productos.</p>";
			return;
		}

		var productos = [];
		for (var i = 0; i < json.datos.length; i++) {
			if (productoEstaActivo(json.datos[i])) {
				productos.push(json.datos[i]);
			}
		}
		productosCatalogo = productos;

		if (productos.length == 0) {
			lista.innerHTML = "<p>No hay productos disponibles.</p>";
			renderizarCategorias([]);
			return;
		}

		renderizarCategorias(productos);
		aplicarFiltroCatalogo();

	} catch (error) {
		lista.innerHTML = "<p>No se pudo conectar con el servidor.</p>";
		renderizarCategorias([]);
	}
}


function categoriaDeProducto(producto) {
	var categoria = String(producto.categoria || "").trim();
	return categoria || "Sin categoria";
}


function contarCategorias(productos) {
	var conteo = {};

	for (var i = 0; i < productos.length; i++) {
		var categoria = categoriaDeProducto(productos[i]);
		if (!conteo[categoria]) conteo[categoria] = 0;
		conteo[categoria] = conteo[categoria] + 1;
	}

	var orden = ["Sonido", "Almacenamiento", "Computo", "Redes", "Gaming", "Televisores", "Wearables", "Accesorios", "Otros", "Sin categoria"];
	var resultado = [];

	for (var j = 0; j < orden.length; j++) {
		var nombre = orden[j];
		if (conteo[nombre]) {
			resultado.push({nombre: nombre, total: conteo[nombre]});
		}
	}

	for (var categoria in conteo) {
		if (orden.indexOf(categoria) === -1) {
			resultado.push({nombre: categoria, total: conteo[categoria]});
		}
	}

	return resultado;
}


function renderizarCatalogo(productos) {
	var lista = document.getElementById("product-list");
	if (!lista) return;

	if (!productos.length) {
		lista.innerHTML = "<p>No hay productos en esta categoria.</p>";
		return;
	}

	var html = "";
	for (var i = 0; i < productos.length; i++) {
		var producto = productos[i];
		html += '<article class="card">';
		html += '<img src="' + producto.imagen + '" alt="' + producto.nombre + '" />';
		html += '<div class="card-body">';
		html += '<h3 class="card-title">' + producto.nombre + '</h3>';
		html += '<p class="price">' + formatoPrecio(producto.precio) + '</p>';
		html += '<div class="actions">';
		html += '<a class="btn btn-secondary" href="detalle.html?id=' + producto.id + '">Ver detalle</a>';
		html += '<button class="btn btn-primary" data-add="' + producto.id + '">Agregar</button>';
		html += '</div></div></article>';
	}
	lista.innerHTML = html;

	var botones = lista.querySelectorAll("[data-add]");
	for (var k = 0; k < botones.length; k++) {
		botones[k].addEventListener("click", function() {
			agregarAlCarrito(Number(this.dataset.add));
		});
	}
}


function actualizarResumenCategorias(totalFiltrados, totalGeneral) {
	var resumen = document.getElementById("category-summary");
	if (!resumen) return;
	var presupuestoNumero = Number(presupuestoCatalogo);
	var tienePresupuesto = presupuestoCatalogo !== "" && !isNaN(presupuestoNumero) && presupuestoNumero >= 0;
	var filtros = [];

	if (categoriaActiva !== "all") {
		filtros.push("categoria " + categoriaActiva);
	}

	if (tienePresupuesto) {
		filtros.push("presupuesto " + formatoPrecio(presupuestoNumero));
}

	if (filtros.length) {
		resumen.textContent = "Mostrando " + totalFiltrados + " productos (" + filtros.join(" | ") + ") de " + totalGeneral + ".";
		return;
	}

	resumen.textContent = "Mostrando " + totalFiltrados + " productos en total.";
}


function resaltarCategoriaActiva() {
	var botones = document.querySelectorAll(".category-btn");
	for (var i = 0; i < botones.length; i++) {
		var activa = botones[i].dataset.category === categoriaActiva;
		botones[i].classList.toggle("is-active", activa);
	}
}


function configurarOrdenCatalogo() {
	var selector = document.getElementById("catalog-order");
	var inputPresupuesto = document.getElementById("catalog-budget");
	if (!selector || !inputPresupuesto) return;

	ordenCatalogo = selector.value || "az";
	presupuestoCatalogo = String(inputPresupuesto.value || "").trim();

	if (!selector.dataset.bound) {
		selector.addEventListener("change", function() {
			ordenCatalogo = this.value || "az";
			aplicarFiltroCatalogo();
		});
		selector.dataset.bound = "1";
	}

	if (!inputPresupuesto.dataset.bound) {
		inputPresupuesto.addEventListener("input", function() {
			presupuestoCatalogo = String(this.value || "").trim();
			aplicarFiltroCatalogo();
		});
		inputPresupuesto.dataset.bound = "1";
	}
}


function aplicarFiltroCatalogo() {
	if (!productosCatalogo.length) {
		renderizarCatalogo([]);
		actualizarResumenCategorias(0, 0);
		return;
	}

	var presupuestoNumero = Number(presupuestoCatalogo);
	var usarPresupuesto = presupuestoCatalogo !== "" && !isNaN(presupuestoNumero) && presupuestoNumero >= 0;

	var filtrados = [];
	for (var i = 0; i < productosCatalogo.length; i++) {
		var producto = productosCatalogo[i];
		if (categoriaActiva !== "all" && categoriaDeProducto(producto) !== categoriaActiva) {
			continue;
		}

		if (usarPresupuesto && Number(producto.precio) > presupuestoNumero) {
			continue;
		}

		filtrados.push(producto);
	}

	filtrados.sort(function(a, b) {
		var precioA = Number(a.precio || 0);
		var precioB = Number(b.precio || 0);
		if (ordenCatalogo === "precio-desc" && precioA !== precioB) return precioB - precioA;
		if (ordenCatalogo === "precio-asc" && precioA !== precioB) return precioA - precioB;

		var nombreA = String(a.nombre || "").toLowerCase();
		var nombreB = String(b.nombre || "").toLowerCase();
		if (nombreA === nombreB) return 0;
		if (ordenCatalogo === "za") return nombreA < nombreB ? 1 : -1;
		return nombreA < nombreB ? -1 : 1;
	});

	renderizarCatalogo(filtrados);
	actualizarResumenCategorias(filtrados.length, productosCatalogo.length);
	resaltarCategoriaActiva();
}


function configurarControlesAdminProductos() {
	var filtroEstado = document.getElementById("admin-estado-filtro");
	var filtroCategoria = document.getElementById("admin-categoria-filtro");
	var ordenNombre = document.getElementById("admin-orden-nombre");
	if (!filtroEstado || !filtroCategoria || !ordenNombre) return;

	adminEstadoFiltro = filtroEstado.value || "all";
	adminCategoriaFiltro = filtroCategoria.value || "all";
	adminOrdenNombre = ordenNombre.value || "az";

	if (!filtroEstado.dataset.bound) {
		filtroEstado.addEventListener("change", function() {
			adminEstadoFiltro = this.value;
			mostrarAdminProductos();
		});
		filtroEstado.dataset.bound = "1";
	}

	if (!ordenNombre.dataset.bound) {
		ordenNombre.addEventListener("change", function() {
			adminOrdenNombre = this.value;
			mostrarAdminProductos();
		});
		ordenNombre.dataset.bound = "1";
	}

	if (!filtroCategoria.dataset.bound) {
		filtroCategoria.addEventListener("change", function() {
			adminCategoriaFiltro = this.value;
			mostrarAdminProductos();
		});
		filtroCategoria.dataset.bound = "1";
	}
}


function poblarCategoriasAdmin(productos) {
	var filtroCategoria = document.getElementById("admin-categoria-filtro");
	if (!filtroCategoria) return;

	var categorias = [];
	for (var i = 0; i < productos.length; i++) {
		var categoria = categoriaDeProducto(productos[i]);
		if (categorias.indexOf(categoria) === -1) categorias.push(categoria);
	}

	categorias.sort(function(a, b) {
		var aMin = String(a || "").toLowerCase();
		var bMin = String(b || "").toLowerCase();
		if (aMin === bMin) return 0;
		return aMin < bMin ? -1 : 1;
	});

	var valorActual = adminCategoriaFiltro || filtroCategoria.value || "all";
	var html = '<option value="all">Todas</option>';
	for (var j = 0; j < categorias.length; j++) {
		html += '<option value="' + categorias[j] + '">' + categorias[j] + '</option>';
	}
	filtroCategoria.innerHTML = html;

	var existeSeleccion = false;
	for (var k = 0; k < filtroCategoria.options.length; k++) {
		if (filtroCategoria.options[k].value === valorActual) {
			existeSeleccion = true;
			break;
		}
	}

	filtroCategoria.value = existeSeleccion ? valorActual : "all";
	adminCategoriaFiltro = filtroCategoria.value;
}


function productosFiltradosYOrdenadosAdmin(productos) {
	var resultado = [];
	for (var i = 0; i < productos.length; i++) {
		var activo = productoEstaActivo(productos[i]);
		var categoria = categoriaDeProducto(productos[i]);

		if (adminEstadoFiltro === "activos" && !activo) continue;
		if (adminEstadoFiltro === "inactivos" && activo) continue;
		if (adminCategoriaFiltro !== "all" && categoria !== adminCategoriaFiltro) continue;

		resultado.push(productos[i]);
	}

	resultado.sort(function(a, b) {
		var nombreA = String(a.nombre || "").toLowerCase();
		var nombreB = String(b.nombre || "").toLowerCase();
		if (nombreA === nombreB) return 0;
		if (adminOrdenNombre === "za") return nombreA < nombreB ? 1 : -1;
		return nombreA < nombreB ? -1 : 1;
	});

	return resultado;
}


function actualizarResumenAdmin(totalFiltrado, totalGeneral) {
	var resumen = document.getElementById("admin-products-summary");
	if (!resumen) return;

	if (adminEstadoFiltro === "activos") {
		resumen.textContent = "Mostrando visibles: " + totalFiltrado + " de " + totalGeneral;
		return;
	}

	if (adminEstadoFiltro === "inactivos") {
		resumen.textContent = "Mostrando inactivos: " + totalFiltrado + " de " + totalGeneral;
		return;
	}

	if (adminCategoriaFiltro !== "all") {
		resumen.textContent = "Categoria " + adminCategoriaFiltro + ": " + totalFiltrado + " de " + totalGeneral;
		return;
	}

	resumen.textContent = "Mostrando todos: " + totalFiltrado + " de " + totalGeneral;
}


function renderizarCategorias(productos) {
	var lista = document.getElementById("category-list");
	if (!lista) return;

	var categorias = contarCategorias(productos);
	var total = productos.length;
	var html = '';
	html += '<li><button class="category-btn" data-category="all"><span>Todas</span><span class="category-count">' + total + '</span></button></li>';

	for (var i = 0; i < categorias.length; i++) {
		html += '<li><button class="category-btn" data-category="' + categorias[i].nombre + '"><span>' + categorias[i].nombre + '</span><span class="category-count">' + categorias[i].total + '</span></button></li>';
	}

	lista.innerHTML = html;

	var botones = lista.querySelectorAll(".category-btn");
	for (var j = 0; j < botones.length; j++) {
		botones[j].addEventListener("click", function() {
			categoriaActiva = this.dataset.category;
			aplicarFiltroCatalogo();
		});
	}

	actualizarResumenCategorias(total, total);
	resaltarCategoriaActiva();
}


function configurarPanelCategorias() {
	var botonAbrir = document.getElementById("toggle-categories");
	var botonCerrar = document.getElementById("close-categories");
	var drawer = document.getElementById("category-drawer");
	var overlay = document.getElementById("category-overlay");

	if (!botonAbrir || !botonCerrar || !drawer || !overlay) return;

	function abrirPanel() {
		drawer.classList.add("is-open");
		drawer.setAttribute("aria-hidden", "false");
		overlay.hidden = false;
		botonAbrir.setAttribute("aria-expanded", "true");
	}

	function cerrarPanel() {
		drawer.classList.remove("is-open");
		drawer.setAttribute("aria-hidden", "true");
		overlay.hidden = true;
		botonAbrir.setAttribute("aria-expanded", "false");
	}

	botonAbrir.addEventListener("click", abrirPanel);
	botonCerrar.addEventListener("click", cerrarPanel);
	overlay.addEventListener("click", cerrarPanel);

	document.addEventListener("keydown", function(event) {
		if (event.key === "Escape") {
			cerrarPanel();
		}
	});
}


async function mostrarDetalle() {
	var contenedor = document.getElementById("detalle-producto");
	if (!contenedor) return;

	var parametros = new URLSearchParams(window.location.search);
	var idProducto = parametros.get("id");
	contenedor.innerHTML = "<p>Cargando...</p>";

	try {
		var respuesta = await fetch(API + "/productos/" + idProducto);
		var json = await respuesta.json();

		if (!json.exito) {
			contenedor.innerHTML = '<section class="empty-state"><p>Producto no encontrado.</p><a class="btn btn-primary" href="index.html">Volver al inicio</a></section>';
			return;
		}

		var producto = json.datos;
		if (!productoEstaActivo(producto)) {
			contenedor.innerHTML = '<section class="empty-state"><p>Producto no disponible en este momento.</p><a class="btn btn-primary" href="index.html">Volver al inicio</a></section>';
			return;
		}

		var p = json.datos;

		var html = '<section class="detail-layout">';
		html += '<img src="' + p.imagen + '" alt="' + p.nombre + '" />';
		html += '<div>';
		html += '<h2>' + p.nombre + '</h2>';
		html += '<p class="price">' + formatoPrecio(p.precio) + '</p>';
		html += '<p>' + p.descripcion + '</p>';
		html += '<ul class="info-list">';
		html += '<li><strong>Marca:</strong> ' + p.marca + '</li>';
		html += '<li><strong>Modelo:</strong> ' + p.modelo + '</li>';
		html += '<li><strong>Tamaño:</strong> ' + p.tamano + '</li>';
		html += '<li><strong>Peso:</strong> ' + p.peso + '</li>';
		html += '<li><strong>Color:</strong> ' + p.color + '</li>';
		html += '<li><strong>Conexión:</strong> ' + p.conexion + '</li>';
		html += '<li><strong>Garantía:</strong> ' + p.garantia + '</li>';
		html += '</ul>';
		html += '<div class="actions">';
		html += '<button class="btn btn-primary" id="add-detail">Agregar al carrito</button>';
		html += '<a class="btn btn-secondary" href="index.html">Regresar</a>';
		html += '</div></div></section>';

		contenedor.innerHTML = html;

		document.getElementById("add-detail").addEventListener("click", function() {
			agregarAlCarrito(p.id);
		});

	} catch (error) {
		contenedor.innerHTML = "<p>No se pudo conectar con el servidor.</p>";
	}
}


function agregarAlCarrito(idProducto) {
	var carrito = obtenerCarrito();
	var encontrado = false;

	for (var i = 0; i < carrito.length; i++) {
		if (carrito[i].id == idProducto) {
			carrito[i].cantidad = carrito[i].cantidad + 1;
			encontrado = true;
			break;
		}
	}

	if (!encontrado) {
		carrito.push({id: idProducto, cantidad: 1});
	}

	guardarCarrito(carrito);
	alert("Producto agregado al carrito.");
}


async function mostrarCarrito() {
	var cuerpoTabla = document.getElementById("cart-body");
	var estadoVacio = document.getElementById("cart-empty");
	var totales = document.getElementById("cart-totals");
	var botonVaciar = document.getElementById("clear-cart");
	var botonCheckout = document.getElementById("checkout-btn");
	if (!cuerpoTabla) return;

	if (botonVaciar && !botonVaciar.dataset.bound) {
		botonVaciar.addEventListener("click", function() {
			if (!confirm("¿Vaciar todo el carrito?")) return;
			vaciarCarrito();
			mostrarCarrito();
		});
		botonVaciar.dataset.bound = "1";
	}

	var carrito = obtenerCarrito();

	if (carrito.length == 0) {
		estadoVacio.hidden = false;
		totales.textContent = "";
		cuerpoTabla.innerHTML = "";
		if (botonCheckout) {
			botonCheckout.classList.add("is-disabled");
			botonCheckout.setAttribute("aria-disabled", "true");
		}
		return;
	}

	estadoVacio.hidden = true;
	cuerpoTabla.innerHTML = "<tr><td colspan='5'>Cargando...</td></tr>";

	try {
		var respuesta = await fetch(API + "/productos?activos=all");
		var json = await respuesta.json();

		if (!json.exito) {
			cuerpoTabla.innerHTML = "<tr><td colspan='5'>Error al cargar.</td></tr>";
			return;
		}

		var productos = json.datos;

		function renderizarCarritoLocal(carritoActual) {
			if (!carritoActual.length) {
				estadoVacio.hidden = false;
				totales.textContent = "";
				cuerpoTabla.innerHTML = "";
				if (botonCheckout) {
					botonCheckout.classList.add("is-disabled");
					botonCheckout.setAttribute("aria-disabled", "true");
				}
				return;
			}

			estadoVacio.hidden = true;
			if (botonCheckout) {
				botonCheckout.classList.remove("is-disabled");
				botonCheckout.removeAttribute("aria-disabled");
			}

			var total = 0;
			var html = "";

			for (var i = 0; i < carritoActual.length; i++) {
				var producto = null;
				for (var j = 0; j < productos.length; j++) {
					if (Number(productos[j].id) === Number(carritoActual[i].id)) {
						producto = productos[j];
						break;
					}
				}
				if (!producto) continue;

				var subtotal = Number(producto.precio) * Number(carritoActual[i].cantidad);
				total = total + subtotal;

				html += "<tr>";
				html += "<td>" + producto.nombre + "</td>";
				html += "<td>" + formatoPrecio(producto.precio) + "</td>";
				html += "<td>";
				html += '<div class="qty-controls">';
				html += '<button class="btn btn-secondary qty-btn" type="button" data-dec="' + carritoActual[i].id + '">-</button>';
				html += '<span class="qty-value">' + carritoActual[i].cantidad + '</span>';
				html += '<button class="btn btn-secondary qty-btn" type="button" data-inc="' + carritoActual[i].id + '">+</button>';
				html += '</div>';
				html += "</td>";
				html += "<td>" + formatoPrecio(subtotal) + "</td>";
				html += '<td><button class="btn btn-danger" type="button" data-remove="' + carritoActual[i].id + '">Eliminar</button></td>';
				html += "</tr>";
			}

			cuerpoTabla.innerHTML = html;

			var envio = 10.00;
			totales.textContent = "Productos: " + formatoPrecio(total) + " | Envio: " + formatoPrecio(envio) + " | Total a pagar: " + formatoPrecio(total + envio);

			var botonesEliminar = cuerpoTabla.querySelectorAll("[data-remove]");
			for (var r = 0; r < botonesEliminar.length; r++) {
				botonesEliminar[r].addEventListener("click", function() {
					eliminarDelCarrito(Number(this.dataset.remove));
					renderizarCarritoLocal(obtenerCarrito());
				});
			}

			var botonesAumentar = cuerpoTabla.querySelectorAll("[data-inc]");
			for (var a = 0; a < botonesAumentar.length; a++) {
				botonesAumentar[a].addEventListener("click", function() {
					cambiarCantidadCarrito(Number(this.dataset.inc), 1);
					renderizarCarritoLocal(obtenerCarrito());
				});
			}

			var botonesDisminuir = cuerpoTabla.querySelectorAll("[data-dec]");
			for (var b = 0; b < botonesDisminuir.length; b++) {
				botonesDisminuir[b].addEventListener("click", function() {
					cambiarCantidadCarrito(Number(this.dataset.dec), -1);
					renderizarCarritoLocal(obtenerCarrito());
				});
			}
		}

		renderizarCarritoLocal(carrito);

	} catch (error) {
		cuerpoTabla.innerHTML = "<tr><td colspan='5'>No se pudo conectar con el servidor.</td></tr>";
	}
}


async function mostrarPago() {
	var cuerpoResumen = document.getElementById("checkout-items");
	var totalResumen = document.getElementById("checkout-total");
	var estadoVacio = document.getElementById("checkout-empty");
	var tarjetaFormulario = document.getElementById("checkout-form-card");
	var formulario = document.getElementById("checkout-form");
	var facturaCliente = document.getElementById("invoice-result");
	if (!cuerpoResumen || !totalResumen || !formulario) return;

	var carrito = obtenerCarrito();
	if (!carrito.length) {
		estadoVacio.hidden = false;
		totalResumen.textContent = "";
		cuerpoResumen.innerHTML = "";
		tarjetaFormulario.hidden = true;
		return;
	}

	totalResumen.textContent = "Cargando resumen...";

	try {
		var respuesta = await fetch(API + "/productos?activos=all");
		var json = await respuesta.json();
		if (!json.exito) {
			totalResumen.textContent = "No se pudo cargar el resumen de compra.";
			return;
		}

		var productos = json.datos || [];
		var itemsCompra = [];
		var subtotal = 0;
		var html = "";

		for (var i = 0; i < carrito.length; i++) {
			var itemCarrito = carrito[i];
			var producto = null;
			for (var j = 0; j < productos.length; j++) {
				if (Number(productos[j].id) === Number(itemCarrito.id)) {
					producto = productos[j];
					break;
				}
			}

			if (!producto) continue;

			var cantidad = Number(itemCarrito.cantidad || 0);
			var precio = Number(producto.precio || 0);
			var subtotalLinea = cantidad * precio;
			subtotal += subtotalLinea;

			itemsCompra.push({
				id: Number(producto.id),
				nombre: String(producto.nombre || "Producto"),
				precio: precio,
				cantidad: cantidad
			});

			html += "<tr>";
			html += "<td>" + producto.nombre + "</td>";
			html += "<td>" + formatoPrecio(precio) + "</td>";
			html += "<td>" + cantidad + "</td>";
			html += "<td>" + formatoPrecio(subtotalLinea) + "</td>";
			html += "</tr>";
		}

		if (!itemsCompra.length) {
			estadoVacio.hidden = false;
			totalResumen.textContent = "";
			cuerpoResumen.innerHTML = "";
			tarjetaFormulario.hidden = true;
			return;
		}

		cuerpoResumen.innerHTML = html;
		var envio = 10;
		var total = subtotal + envio;
		totalResumen.textContent = "Productos: " + formatoPrecio(subtotal) + " | Envio: " + formatoPrecio(envio) + " | Total: " + formatoPrecio(total);

		var metodoPagoSelect = document.getElementById("checkout-metodo");
		var paypalCampos = document.getElementById("paypal-fields");
		var paypalCorreoInput = document.getElementById("checkout-paypal-email");
		var tarjetaCampos = document.getElementById("card-fields");
		var numeroTarjetaInput = document.getElementById("checkout-card-number");
		var nombreTitularInput = document.getElementById("checkout-card-name");
		var vencimientoInput = document.getElementById("checkout-card-expiry");
		var cvvInput = document.getElementById("checkout-card-cvv");

		if (vencimientoInput && !vencimientoInput.dataset.bound) {
			vencimientoInput.addEventListener("input", function() {
				var digitos = String(this.value || "").replace(/\D/g, "").slice(0, 6);
				if (digitos.length <= 2) {
					this.value = digitos;
					return;
				}
				this.value = digitos.slice(0, 2) + "/" + digitos.slice(2);
			});
			vencimientoInput.dataset.bound = "1";
		}

		function actualizarCamposPago() {
			var metodo = metodoPagoSelect ? metodoPagoSelect.value : "";
			var esTarjeta = metodo === "tarjeta";
			var esPaypal = metodo === "paypal";

			if (paypalCampos) paypalCampos.hidden = !esPaypal;
			if (paypalCorreoInput) paypalCorreoInput.required = esPaypal;

			if (tarjetaCampos) tarjetaCampos.hidden = !esTarjeta;
			if (numeroTarjetaInput) numeroTarjetaInput.required = esTarjeta;
			if (nombreTitularInput) nombreTitularInput.required = esTarjeta;
			if (vencimientoInput) vencimientoInput.required = esTarjeta;
			if (cvvInput) cvvInput.required = esTarjeta;
		}

		if (metodoPagoSelect && !metodoPagoSelect.dataset.bound) {
			metodoPagoSelect.addEventListener("change", actualizarCamposPago);
			metodoPagoSelect.dataset.bound = "1";
		}
		actualizarCamposPago();
		formulario.noValidate = true;

		if (!formulario.dataset.boundSubmit) {
			formulario.addEventListener("submit", async function(evento) {
			evento.preventDefault();
			mostrarErrorPago("");

			var botonConfirmar = formulario.querySelector('button[type="submit"]');
			if (botonConfirmar) {
				botonConfirmar.disabled = true;
				botonConfirmar.textContent = "Procesando...";
			}

			var nombre = String(document.getElementById("checkout-nombre").value || "").trim();
			var direccion = String(document.getElementById("checkout-direccion").value || "").trim();
			var telefono = String(document.getElementById("checkout-telefono").value || "").trim();
			var metodoPago = String(document.getElementById("checkout-metodo").value || "").trim();
			var paypalCorreo = String(document.getElementById("checkout-paypal-email").value || "").trim();
			var numeroTarjeta = String(document.getElementById("checkout-card-number").value || "").trim();
			var nombreTitular = String(document.getElementById("checkout-card-name").value || "").trim();
			var vencimiento = String(document.getElementById("checkout-card-expiry").value || "").trim();
			var cvv = String(document.getElementById("checkout-card-cvv").value || "").trim();
			var aceptaTerminos = !!document.getElementById("checkout-terms") && document.getElementById("checkout-terms").checked;

			if (!nombre || !direccion || !telefono || !metodoPago) {
				mostrarErrorPago("Completa todos los campos del formulario de pago.");
				if (botonConfirmar) {
					botonConfirmar.disabled = false;
					botonConfirmar.textContent = "Confirmar compra";
				}
				return;
			}

			if (!aceptaTerminos) {
				mostrarErrorPago("Debes aceptar los términos y condiciones para continuar.");
				if (botonConfirmar) {
					botonConfirmar.disabled = false;
					botonConfirmar.textContent = "Confirmar compra";
				}
				return;
			}

			if (metodoPago === "paypal") {
				if (!validarCorreo(paypalCorreo)) {
					mostrarErrorPago("Ingresa un correo valido para PayPal.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}
			}

			if (metodoPago === "tarjeta") {
				if (!validarNumeroTarjeta(numeroTarjeta)) {
					mostrarErrorPago("Numero de tarjeta invalido. Debe tener entre 13 y 19 digitos y pasar validacion.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}

				if (!validarNombreTitular(nombreTitular)) {
					mostrarErrorPago("Nombre del titular invalido. Usa solo letras y espacios, minimo 3 caracteres.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}

				if (!validarFechaVencimiento(vencimiento)) {
					mostrarErrorPago("Fecha de vencimiento invalida. Usa formato MM/YYYY y una fecha no vencida.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}

				if (!validarCvv(cvv)) {
					mostrarErrorPago("CVV invalido. Debe contener 3 o 4 digitos numericos.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}
			}

			var sesion = obtenerSesion();

			try {
				var respuestaCompra = await fetch(API + "/facturas", {
					method: "POST",
					headers: {"Content-Type": "application/json"},
					body: JSON.stringify({
						nombre: nombre,
						direccion: direccion,
						telefono: telefono,
						metodo_pago: metodoPago,
						paypal_correo: paypalCorreo,
						usuario: sesion ? (sesion.nombre || sesion.usuario || "") : "",
						items: itemsCompra
					})
				});

				var jsonCompra = await respuestaCompra.json();
				if (!respuestaCompra.ok || !jsonCompra.exito) {
					mostrarErrorPago(jsonCompra.mensaje || "No se pudo completar la compra.");
					if (botonConfirmar) {
						botonConfirmar.disabled = false;
						botonConfirmar.textContent = "Confirmar compra";
					}
					return;
				}

				vaciarCarrito();
				tarjetaFormulario.hidden = true;
				facturaCliente.hidden = false;

				var factura = jsonCompra.factura;
				var filas = "";
				for (var x = 0; x < factura.items.length; x++) {
					filas += "<tr>";
					filas += "<td>" + factura.items[x].nombre + "</td>";
					filas += "<td>" + formatoPrecio(factura.items[x].precio) + "</td>";
					filas += "<td>" + factura.items[x].cantidad + "</td>";
					filas += "<td>" + formatoPrecio(factura.items[x].subtotal) + "</td>";
					filas += "</tr>";
				}

				facturaCliente.innerHTML = "";
				facturaCliente.innerHTML += "<h2>Factura para el cliente</h2>";
				facturaCliente.innerHTML += "<p><strong>Número de factura:</strong> " + factura.numero_factura + "</p>";
				facturaCliente.innerHTML += "<p><strong>Fecha:</strong> " + factura.fecha + "</p>";
				facturaCliente.innerHTML += "<p><strong>Cliente:</strong> " + factura.nombre + "</p>";
				facturaCliente.innerHTML += "<p><strong>Dirección:</strong> " + factura.direccion + "</p>";
				facturaCliente.innerHTML += "<p><strong>Teléfono:</strong> " + factura.telefono + "</p>";
				facturaCliente.innerHTML += "<p><strong>Método de pago:</strong> " + (factura.metodo_pago === "paypal" ? "PayPal" : "Tarjeta de crédito") + "</p>";
				facturaCliente.innerHTML += '<div class="table-wrap" style="margin-top:12px;"><table><thead><tr><th>Producto</th><th>Precio</th><th>Cantidad</th><th>Subtotal</th></tr></thead><tbody>' + filas + '</tbody></table></div>';
				facturaCliente.innerHTML += "<p style='margin-top:10px;'><strong>Subtotal:</strong> " + formatoPrecio(factura.subtotal) + "</p>";
				facturaCliente.innerHTML += "<p><strong>Envío:</strong> " + formatoPrecio(factura.envio) + "</p>";
				facturaCliente.innerHTML += "<p><strong>Total:</strong> " + formatoPrecio(factura.total) + "</p>";
				facturaCliente.innerHTML += '<a href="index.html" class="btn btn-primary">Seguir comprando</a>';

				cuerpoResumen.innerHTML = "";
				totalResumen.textContent = "Compra completada con éxito.";
			} catch (errorCompra) {
				mostrarErrorPago("No se pudo conectar con el servidor para completar el pago.");
				if (botonConfirmar) {
					botonConfirmar.disabled = false;
					botonConfirmar.textContent = "Confirmar compra";
				}
			}
			});
			formulario.dataset.boundSubmit = "1";
		}
	} catch (error) {
		totalResumen.textContent = "No se pudo conectar con el servidor.";
	}
}


function configurarLogin() {
	var formulario = document.getElementById("login-form");
	if (!formulario) return;

	var inputUsuario = document.getElementById("usuario");
	var inputPassword = document.getElementById("password");

	formulario.addEventListener("submit", async function(e) {
		e.preventDefault();

		if (!inputUsuario.value || !inputPassword.value) {
			alert("Completa todos los campos.");
			return;
		}

		try {
			var respuesta = await fetch(AUTH_API + "/login", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify({
					username: inputUsuario.value.trim(),
					password: inputPassword.value.trim()
				})
			});
			var json = await respuesta.json();

			if (respuesta.ok) {
				guardarSesion({
					usuario: json.nombre || inputUsuario.value.trim(),
					nombre: json.nombre || inputUsuario.value.trim(),
					rol: json.rol || "usuario",
					correo: json.correo || "",
					telefono: json.telefono || ""
				});

				if ((json.rol || "").toLowerCase() === "admin") {
					window.location.href = "producto.html";
				} else {
					window.location.href = "index.html";
				}
			} else {
				alert(json.mensaje || "No se pudo iniciar sesion.");
			}
		} catch (error) {
			alert("Error de conexion.");
		}
	});
}


async function mostrarAdminProductos() {
	var cuerpoTabla = document.getElementById("admin-products-body");
	if (!cuerpoTabla) return;

	if (!requiereAdmin()) return;
	configurarControlesAdminProductos();

	cuerpoTabla.innerHTML = "<tr><td colspan='4'>Cargando...</td></tr>";

	try {
		var respuesta = await fetch(API + "/productos?activos=all");
		var json = await respuesta.json();

		if (!json.exito) {
			cuerpoTabla.innerHTML = "<tr><td colspan='4'>Error al cargar productos.</td></tr>";
			return;
		}

		poblarCategoriasAdmin(json.datos || []);
		var productos = productosFiltradosYOrdenadosAdmin(json.datos || []);
		actualizarResumenAdmin(productos.length, (json.datos || []).length);

		if (!productos.length) {
			cuerpoTabla.innerHTML = "<tr><td colspan='4'>No hay productos para ese filtro.</td></tr>";
			return;
		}

		var html = "";

		for (var i = 0; i < productos.length; i++) {
			var producto = productos[i];
			var estado = producto.activo ? "Activo" : "Inactivo";
			var clase = producto.activo ? "active" : "inactive";

			html += "<tr>";
			html += "<td>" + producto.nombre + "</td>";
			html += "<td>" + formatoPrecio(producto.precio) + "</td>";
			html += '<td><span class="status ' + clase + '">' + estado + '</span></td>';
			html += '<td class="inline-actions">';
			html += '<a class="btn btn-secondary" href="editarProducto.html?id=' + producto.id + '">Editar</a>';
			html += '<button class="btn btn-danger" data-delete="' + producto.id + '">Eliminar</button>';
			html += '</td></tr>';
		}
		cuerpoTabla.innerHTML = html;

		var botonesEliminar = cuerpoTabla.querySelectorAll("[data-delete]");
		for (var i = 0; i < botonesEliminar.length; i++) {
			botonesEliminar[i].addEventListener("click", async function() {
				if (!confirm("Eliminar este producto?")) return;
				await fetch(API + "/productos/" + this.dataset.delete, {method: "DELETE"});
				mostrarAdminProductos();
			});
		}

	} catch (error) {
		cuerpoTabla.innerHTML = "<tr><td colspan='4'>No se pudo conectar con el servidor.</td></tr>";
	}
}


function configurarNuevoProducto() {
	var formulario = document.getElementById("new-product-form");
	if (!formulario) return;

	if (!requiereAdmin()) return;

	formulario.addEventListener("submit", async function(e) {
		e.preventDefault();

		var producto = {
			nombre: formulario.nombre.value,
			marca: formulario.marca.value,
			modelo: formulario.modelo.value,
			categoria: formulario.categoria.value,
			precio: Number(formulario.precio.value),
			descripcion: formulario.descripcion.value,
			tamano: formulario.tamano.value,
			peso: formulario.peso.value,
			color: formulario.color.value,
			conexion: formulario.conexion.value,
			garantia: formulario.garantia.value,
			imagen: formulario.imagen.value,
			activo: formulario.activo.value === "true"
		};

		if (!producto.nombre || !producto.categoria || !producto.precio || !producto.descripcion) {
			alert("Completa los campos requeridos.");
			return;
		}

		try {
			var respuesta = await fetch(API + "/productos", {
				method: "POST",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify(producto)
			});
			var json = await respuesta.json();
			alert(json.mensaje);
			if (json.exito) window.location.href = "producto.html";
		} catch (error) {
			alert("Error de conexion.");
		}
	});
}


async function configurarEditarProducto() {
	var formulario = document.getElementById("edit-product-form");
	if (!formulario) return;

	if (!requiereAdmin()) return;

	var parametros = new URLSearchParams(window.location.search);
	var id = parametros.get("id");

	try {
		var respuesta = await fetch(API + "/productos/" + id);
		var json = await respuesta.json();

		if (!json.exito) {
			alert("Producto no encontrado.");
			window.location.href = "producto.html";
			return;
		}

		var p = json.datos;

		formulario.nombre.value = p.nombre;
		formulario.marca.value = p.marca || "";
		formulario.modelo.value = p.modelo || "";
		formulario.categoria.value = p.categoria || "Otros";
		formulario.precio.value = p.precio;
		formulario.descripcion.value = p.descripcion;
		formulario.tamano.value = p.tamano || "";
		formulario.peso.value = p.peso || "";
		formulario.color.value = p.color || "";
		formulario.conexion.value = p.conexion || "";
		formulario.garantia.value = p.garantia || "";
		formulario.imagen.value = p.imagen || "";
		formulario.activo.value = String(p.activo);

		formulario.addEventListener("submit", async function(e) {
			e.preventDefault();

			var actualizado = {
				nombre: formulario.nombre.value,
				marca: formulario.marca.value,
				modelo: formulario.modelo.value,
				categoria: formulario.categoria.value,
				precio: Number(formulario.precio.value),
				descripcion: formulario.descripcion.value,
				tamano: formulario.tamano.value,
				peso: formulario.peso.value,
				color: formulario.color.value,
				conexion: formulario.conexion.value,
				garantia: formulario.garantia.value,
				imagen: formulario.imagen.value,
				activo: formulario.activo.value === "true"
			};

			var respuesta2 = await fetch(API + "/productos/" + id, {
				method: "PUT",
				headers: {"Content-Type": "application/json"},
				body: JSON.stringify(actualizado)
			});
			var json2 = await respuesta2.json();
			alert(json2.mensaje);
			if (json2.exito) window.location.href = "producto.html";
		});

	} catch (error) {
		alert("Error de conexion.");
		window.location.href = "producto.html";
	}
}


actualizarNav();

if (pagina === "index") {
	configurarPanelCategorias();
	configurarOrdenCatalogo();
	mostrarCatalogo();
}
if (pagina === "detalle") mostrarDetalle();
if (pagina === "carrito") mostrarCarrito();
if (pagina === "pago") mostrarPago();
if (pagina === "login") configurarLogin();
if (pagina === "registro") configurarRegistro();
if (pagina === "producto") mostrarAdminProductos();
if (pagina === "nuevo-producto") configurarNuevoProducto();
if (pagina === "editar-producto") configurarEditarProducto();
