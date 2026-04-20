CREATE DATABASE tecno_city_zone;

USE tecno_city_zone;

CREATE TABLE usuarios (
  id        INT AUTO_INCREMENT PRIMARY KEY,
  username  VARCHAR(50) NOT NULL UNIQUE,
  telefono  VARCHAR(20) NOT NULL UNIQUE,
  password  VARCHAR(255) NOT NULL,
  rol       VARCHAR(20) NOT NULL DEFAULT 'usuario',
  nombre    VARCHAR(100) NOT NULL,
  correo    VARCHAR(150) NOT NULL UNIQUE,
  edad      INT NOT NULL,
  activo    BOOLEAN DEFAULT TRUE
);

CREATE TABLE productos (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nombre      VARCHAR(150) NOT NULL,
  marca       VARCHAR(100),
  modelo      VARCHAR(100),
  categoria   VARCHAR(80) NOT NULL DEFAULT 'Sin categoria',
  precio      DECIMAL(10,2) NOT NULL,
  descripcion TEXT NOT NULL,
  tamano      VARCHAR(50),
  peso        VARCHAR(50),
  color       VARCHAR(50),
  conexion    VARCHAR(100),
  garantia    VARCHAR(50),
  imagen      VARCHAR(500),
  activo      BOOLEAN DEFAULT TRUE
);

INSERT INTO usuarios (username, telefono, password, rol, nombre, correo, edad) VALUES
('admin', '00000000', '1234', 'admin', 'admin', 'admin@tecno.com', 18);

INSERT INTO productos (nombre, marca, modelo, categoria, precio, descripcion, tamano, peso, color, conexion, garantia, imagen, activo) VALUES
('Teclado Mecánico RGB', 'Redragon', 'K552', 'Computo', 75.00, 'Teclado mecánico compacto con iluminación RGB y switches táctiles.', '60%', '0.9 kg', 'Blanco', 'USB', '12 meses', 'https://m.media-amazon.com/images/I/71FSIp+tDNL._AC_SL1000__.jpg', 1),
('Mouse Gamer G502', 'Logitech', 'G502 Hero', 'Gaming', 60.00, 'Mouse ergonómico para alto rendimiento.', '13 cm', '0.3 kg', 'Blanco', 'USB', '12 meses', 'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80', 1),
('Audífonos Pro', 'Sony', 'WH-1000XM4', 'Sonido', 95.00, 'Audio de alta fidelidad con cancelación de ruido.', 'Circumaural', '0.5 kg', 'Negro', 'Bluetooth / Jack 3.5 mm', '12 meses', 'https://www.sony.com.hn/image/5f1b97d4867bd54628b3a20c4b088945?fmt=pjpeg&wid=1400&bgcolor=F1F5F9&bgc=F1F5F9', 1),
('Laptop Ultra 14', 'HP', 'IdeaPad 5', 'Computo', 899.00, 'Laptop liviana para estudio y trabajo diario.', '14 pulgadas', '1.4 kg', 'Gris', 'Wi-Fi 6 / Bluetooth', '12 meses', 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80', 1),
('Webcam Full HD', 'Logitech', 'C920', 'Computo', 45.00, 'Cámara web 1080p para videollamadas y streaming.', '30 cm', '0.2 kg', 'Negro', 'USB', '12 meses', 'https://www.kelyx.com.ar/images/000000000041730228266webcam-kelyx-1.jpg', 1),
('Silla Ergonómica', 'ErgoSeat', 'SE100', 'Accesorios', 180.00, 'Silla cómoda para largas jornadas frente al escritorio.', 'Ajustable', '12 kg', 'Negro', 'No aplica', '24 meses', 'https://http2.mlstatic.com/D_Q_NP_832051-MLA84655422253_052025-F.webp', 1),
('Micro SD', 'Maxell', 'ActionPro A1 V30', 'Almacenamiento', 18.00, 'Tarjeta microSD de alta velocidad ideal para grabación en 4K y cámaras de acción.', '128 GB', '0.01 kg', 'Negra', 'MicroSDXC UHS-I', '12 meses', 'https://www.tiendasekono.com/media/catalog/product/3/4/348156.jpeg?quality=80&bg-color=255,255,255&fit=bounds&height=1080&width=1080&canvas=1080:1080', 1),
('Speaker Bluetooth', 'JBL', 'Flip 6', 'Sonido', 70.00, 'Parlante portátil con sonido envolvente.', '4 pulgadas', '0.8 kg', 'Negro de colores rgb', 'Bluetooth', '12 meses', 'https://images.unsplash.com/photo-1589003077984-894e133dabab?auto=format&fit=crop&w=900&q=80', 1),
('Smartwatch Fit', 'Xiaomi', 'Mi Watch Lite', 'Wearables', 130.00, 'Reloj inteligente con métricas de salud y deporte.', '50 mm', '0.1 kg', 'Blanco', 'Bluetooth', '12 meses', 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80', 1),
('Televisor', 'Samsung', 'smart tv', 'Televisores', 100.00, 'El Hisense Smart TV UHD de 32 pulgadas modelo 32A4NV es la opción perfecta para quienes buscan un televisor compacto, moderno y con gran calidad de imagen. Su resolución UHD ofrece colores más definidos y detalles nítidos, mientras que el sistema operativo VIDAA te permite acceder fácilmente a tus aplicaciones favoritas como Netflix, YouTube y Prime Video con una navegación rápida y sencilla.', '32', '60', 'negro', 'Usb,Hdmi,Display Port', '2', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_HIS_32A4NV_6870c53fe5cef-1200x1200.webp&w=1080&q=75', 1),
('Teclado Inalambrico', 'Logitech', 'K380', 'Computo', 40.00, 'Teclado inalambrico ergonomico ideal para oficina y uso diario.', 'Compacto', '0.5 kg', 'Negro', 'USB / Bluetooth', '12 meses', 'https://resource.logitech.com/w_544,h_544,ar_1,c_fill,q_auto,f_auto,dpr_1.0/d_transparent.gif/content/dam/logitech/en/products/keyboards/alto-keys-k98m/gallery/graphite/alto-keys-k98m-graphite-gallery-lifestyle1.jpg', 1),
('Router WiFi 6', 'TP-Link', 'Archer AX50', 'Redes', 120.00, 'Router de alta velocidad ideal para hogares y pequenas oficinas.', '20 cm', '0.7 kg', 'Negro', 'Wi-Fi', '12 meses', 'https://m.media-amazon.com/images/I/61nKxpRIIpL._AC_UF894,1000_QL80_.jpg', 1),
('Monitor', 'Apple', 'a1407', 'Computo', 210.00, 'Monitor Full HD con excelente calidad de imagen para trabajo y entretenimiento.', '24 pulgadas', '3.5 kg', 'blanco', 'HDMI / USB-C', '12 meses', 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80', 1),
('Disco Duro Externo', 'Seagate', 'Expansion', 'Almacenamiento', 85.00, 'Disco duro externo portatil para almacenamiento seguro.', '1 TB', '0.4 kg', 'Negro', 'USB', '12 meses', 'https://m.media-amazon.com/images/I/61rp7GucANL.jpg', 1),
('Memoria USB', 'Kingston', 'DataTraveler', 'Almacenamiento', 15.00, 'Memoria USB de alta velocidad para transportar archivos facilmente.', '64 GB', '0.02 kg', 'Negro', 'USB', '12 meses', 'https://tecnocomphn.com/wp-content/uploads/2024/06/650e1461089f3097109986.webp', 1),
('Audifonos Bluetooth', 'Sony', 'WF-C500', 'Sonido', 65.00, 'Audifonos inalambricos con sonido envolvente y bateria de larga duracion.', 'Compacto', '0.1 kg', 'blancos', 'Bluetooth', '12 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_HONOR_EARBUDS_X7I_688b0ca8a3cd6-1200x1200.webp&w=1080&q=75', 1),
('Tablet Android', 'Samsung', 'Galaxy Tab A8', 'Computo', 220.00, 'Tablet ligera ideal para entretenimiento, lectura y estudio.', '10 pulgadas', '0.6 kg', 'Gris', 'USB-C', '12 meses', 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?auto=format&fit=crop&w=900&q=80', 1),
('Impresora Multifuncional', 'HP', 'DeskJet 2775', 'Computo', 95.00, 'Impresora multifuncional para imprimir, escanear y copiar documentos.', 'Estandar', '5 kg', 'Negro', 'USB', '12 meses', 'https://copyfaxcor.com/wp-content/uploads/2021/10/Para-qu%C3%A9-sirve-una-impresora-multifuncional.jpg', 1),
('Microfono USB', 'Blue', 'Yeti', 'Sonido', 140.00, 'Microfono profesional para streaming, grabaciones y podcasts.', '20 cm', '1 kg', 'Negro', 'USB / Jack 3.5 mm', '12 meses', 'https://mla-s1-p.mlstatic.com/933281-MLA83018332121_032025-F.jpg', 1),
('Control Gamer', 'Microsoft', 'Xbox Series Controller', 'Gaming', 75.00, 'Control inalambrico compatible con PC y consolas.', '15 cm', '0.3 kg', 'azul', 'Bluetooth', '12 meses', 'https://i.blogs.es/efba30/jumpstory-download20200723-143317/1366_2000.jpg', 1),
('Laptop ASUS VivoBook 14" Intel Core i5 120U / 8GB RAM / 512GB SSD', 'ASUS', 'ASUS-VIVOBOOK14(I5)', 'Computo', 14495.00, 'La ASUS VivoBook 14 combina rendimiento y estilo en un diseño compacto. Equipada con procesador Intel Core i5 120U, 8GB de RAM y SSD de 512GB, ofrece velocidad y eficiencia para trabajo, estudio y entretenimiento.', '32.4 x 21.6 x 1.9 cm', '1.4 kg', 'Plata/Gris', 'Wi-Fi / Bluetooth / Puertos USB-C, USB-A, HDMI, jack de audio', '18 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_ASUS_VIVOBOOK14_I5_697b9f2a15533-1200x1200.webp&w=2048&q=75', 1),
('Audífonos Cubitt Power Headphones Inalámbricos Azul', 'Cubitt', 'CT-PWANC2', 'Sonido', 1295.00, 'Audífonos inalámbricos Cubitt Power Headphones con diseño over-ear en color azul. Ofrecen sonido potente, comodidad prolongada y conexión Bluetooth para disfrutar música sin cables.', '20 x 18 x 8 cm', '0.25 kg', 'Azul', 'Bluetooth inalámbrico, puerto de carga USB', '6 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_CT_PWANC2_6939efd089394-1200x1200.webp&w=2048&q=75', 1),
('Consola Nintendo Switch Neon + Super Mario Bros. Wonder', 'Nintendo', 'HRD-S-KAB1C', 'Gaming', 11995.00, 'La Nintendo Switch Neon incluye los Joy-Con rojo y azul, junto con el juego Super Mario Bros. Wonder. Disfruta de la versatilidad de jugar en casa o en modo portátil con gráficos vibrantes y diversión asegurada.', '24cm x 10cm x 1.4cm', '0.398 kg', 'Negro con controles Neon (rojo y azul)', 'Wi-Fi/Bluetooth/USB-C', '12 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_HRD_S_KAB1C_68f7eda5f223b-1200x1200.webp&w=2048&q=75', 1),
('Memoria Kingston DataTraveler Exodia 128GB Negro', 'Kingston', 'DTX/128GB', 'Almacenamiento', 595.00, 'La memoria USB Kingston DataTraveler Exodia ofrece 128GB de almacenamiento portátil con diseño práctico y tapa protectora. Ideal para transportar y compartir archivos de manera rápida y segura.', '21.04 mm', '0.011kg', 'Negro y Amarillo', 'USB 3.2', '12 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_DTX_128GB_69611e5cae3c4-1200x1200.webp&w=2048&q=75', 1),
('Licencia de Antivirus Kaspersky Estándar 1 año / 3 Dispositivos', 'Kaspersky', 'KSTD3', 'Otros', 1495.00, 'El Antivirus Kaspersky Standard ofrece herramientas avanzadas de protección integral para tus dispositivos, garantizando seguridad contra virus, malware y amenazas en línea.', 'No Aplica', 'No Aplica', 'Azul', 'Activación en línea mediante código de licencia', '12 meses', 'https://jetstereo-retail.s3.us-east-2.amazonaws.com/images/catalog/public/products/product_KSTD3_6870caee469a2.webp', 1),
('Monitor Dell 27" FHD Blanco', 'Dell', 'S2725H-JS', 'Computo', 6695.00, 'Monitor Dell de 27 pulgadas con resolución Full HD, diseño elegante en color blanco y base estilizada. Ideal para trabajo, estudio y entretenimiento gracias a su pantalla amplia y nítida.', '68.6cm', '4.5kg', 'Blanco', 'Alambrica', '12 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_S2725H_JS_68c1bb36d4413-1200x1200.webp&w=2048&q=75', 1),
('Control Backbone One para iPhone (Blanco)', 'Backbone', 'Backbone One (PlayStation Edition)', 'Gaming', 2995.00, 'Control diseñado para transformar tu iPhone en una consola portátil, con diseño inspirado en el mando DualSense de PlayStation, muy cómodo y ligero.', '18cm', '0.138 kg', 'Blanco', 'Inalambrica', '12 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_BB_02_W_S_6870f9498126f-1200x1200.webp&w=2048&q=75', 1),
('Parlante Inteligente', 'Amazon', 'Amazon Echo Dot (5ª Generación)', 'Sonido', 1995.00, 'Parlante inteligente Amazon Echo Dot 5ta Generación: sonido mejorado, diseño compacto y control por voz con Alexa. Ideal para música, automatización del hogar y asistencia diaria.', '100 mm', '0.304kg', 'Azul', 'Wi-Fi/Bluetooth', '6 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_ECHO_DOT5_BLUE_6870ff9e7d5c3-1200x1200.webp&w=2048&q=75', 1),
('Camara Canon EOS Rebel', 'Canon', 'Rebel T7', 'Otros', 19700.00, 'La Canon EOS Rebel T7 combina calidad profesional y facilidad de uso en un diseño ligero. Con sensor de 24.1 MP, grabación Full HD y conectividad alámbrica, es ideal para capturar tus mejores momentos con nitidez y detalle.', '99.7 mm', '0.75 kg', 'Negro', 'Alambrica', '6 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_EOS_REBEL_T7_KIT_6870f106de5d2-1200x1200.webp&w=2048&q=75', 1),
('Laptop MacBook', 'Apple', 'MacBook Air 13', 'Computo', 24995.00, 'Ligera y portátil, ideal para llevar a clases o bibliotecas también cuenta con excelente rendimiento para aplicaciones educativas y multitarea.', '30.41 cm', '2.8 lbs', 'Gris Espacial', 'Wi-Fi 6 / Bluetooth', '9 meses', 'https://www.jetstereo.com/_next/image?url=https%3A%2F%2Fjetstereo-retail.s3.us-east-2.amazonaws.com%2Fimages%2Fcache%2Fcatalog%2Fpublic%2Fproducts%2Fproduct_MGN63LL_A_695e9843a1a2e-1200x1200.webp&w=2048&q=75', 1),
('Computadora de Escritorio', 'Apple', 'iMac', 'Computo', 1299.00, 'Computadora de escritorio todo en uno con pantalla Retina ideal para trabajo, diseño y uso profesional.', '24 pulgadas', '4.5 kg', 'Plata', 'USB-C / Thunderbolt', '12 meses', 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=900&q=80', 1);

UPDATE productos
SET categoria = CASE
  WHEN LOWER(nombre) LIKE '%micro sd%' OR LOWER(nombre) LIKE '%memoria usb%' OR LOWER(nombre) LIKE '%disco%' THEN 'Almacenamiento'
  WHEN LOWER(nombre) LIKE '%audifono%' OR LOWER(nombre) LIKE '%audio%' OR LOWER(nombre) LIKE '%speaker%' OR LOWER(nombre) LIKE '%microfono%' THEN 'Sonido'
  WHEN LOWER(nombre) LIKE '%teclado%' OR LOWER(nombre) LIKE '%mouse%' OR LOWER(nombre) LIKE '%laptop%' OR LOWER(nombre) LIKE '%monitor%' OR LOWER(nombre) LIKE '%tablet%' OR LOWER(nombre) LIKE '%webcam%' OR LOWER(nombre) LIKE '%impresora%' THEN 'Computo'
  WHEN LOWER(nombre) LIKE '%router%' THEN 'Redes'
  WHEN LOWER(nombre) LIKE '%smartwatch%' OR LOWER(nombre) LIKE '%reloj%' THEN 'Wearables'
  WHEN LOWER(nombre) LIKE '%tv%' OR LOWER(nombre) LIKE '%televisor%' THEN 'Televisores'
  WHEN LOWER(nombre) LIKE '%gamer%' OR LOWER(nombre) LIKE '%control%' THEN 'Gaming'
  WHEN LOWER(nombre) LIKE '%silla%' THEN 'Accesorios'
  ELSE 'Otros'
END;

UPDATE productos
SET activo = 1;

