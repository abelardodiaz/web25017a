vamos a hacer unos ajustes al plan, voy a necesitar una area backend donde yo pueda elegir que articulos se van a mostrar en el catalogo de productos, es decir en el area de administracion del sistema por ahora ya tenemos estas funciones principales:
-consultar productos, mostrarlos en forma de lista sin fotos
-realizar busquedas de productos y categorias, y marcas
-administrar productos (añadir manualmente, eliminar, editar, visible o no visible en el catalogo)
-en editar podre revisar los precios, habra un campo de  precio mayoreo (viene de syscom) , margen (alimentado manualmente en terminos de porcentaje), descuento (manualmente y expresado en %) y precio publico (calculado automaticamente , precio mayoreo, mas margen, menos descuento, pero con opcion a editarlo manualmente)
-sincronizar productos, los que esten visibles en el catalogo deberan sincronizarse automaticamente en precio y existencias totales, ayudame a pensar cuantas veces al dia deberan sincronizarse, o como optimizar el uso de estos recursos, probablemente solo sincronizen los campos mas importantes

olvide mencionar que en el area de administracion podremos indicar que nuevos productos añadir a la base de datos, por medio de busqueda (palabra clave) agregaremos varios, o por medio de la ID de un producto en especifico

por ahora no es necesario agregar seguridad o inicios de sesion al sistema

vamos a trabajar en esto antes de migrar a mysql