from datetime import datetime
import flet as ft
import requests

# URL base de tu API Flask
API_BASE_URL = "http://38.224.68.171:5003"


def main(page: ft.Page):
  page.title = "Pedidos Droguería"
  page.vertical_alignment = ft.MainAxisAlignment.CENTER
  page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
  page.bgcolor = "#f4f7f6"
  page.padding = 20

  usuario_actual = {}
  pedido_actual = {"id_cliente": None, "razon_social": "", "ruc": "", "items": []}

  def mostrar_alerta(mensaje, es_error=True):
    page.snack_bar = ft.SnackBar(
        content=ft.Text(mensaje, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.RED_400 if es_error else ft.Colors.GREEN_400,
    )
    page.snack_bar.open = True
    page.update()

  # ==================== DETALLE DE DEUDAS ====================
  def mostrar_detalle_deuda(id_cliente, nombre_cliente):
    columna_resultados = ft.Column(
        [
            ft.ProgressRing(),
            ft.Text("Cargando detalle de facturas...", size=12, color=ft.Colors.GREY_700),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    contenedor_dialogo = ft.Container(
        content=columna_resultados, width=420, height=320, alignment=ft.alignment.center
    )

    def cerrar_dialogo(e):
      dlg_detalle.open = False
      page.update()

    dlg_detalle = ft.AlertDialog(
        title=ft.Text(
            f"Facturas de: {nombre_cliente}",
            size=14,
            weight=ft.FontWeight.BOLD,
        ),
        content=contenedor_dialogo,
        actions=[ft.TextButton("Cerrar", on_click=cerrar_dialogo)],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dlg_detalle)
    dlg_detalle.open = True
    page.update()

    async def ejecutar_carga_detalle():
      try:
        response = requests.get(
            f"{API_BASE_URL}/api/hoja_ruta/detalle",
            params={"id_cliente": str(id_cliente)},
            timeout=10,
        )

        lista_facturas = ft.ListView(expand=1, spacing=8, padding=5)

        if response.status_code == 200:
          facturas = response.json()
          if facturas and isinstance(facturas, list):
            for fac in facturas:
              nro_comprobante = (
                  fac.get("Comprobante")
                  or fac.get("No_Comprobante")
                  or "N/D"
              )
              fecha_emision = fac.get("F_Emision") or fac.get("Fecha_Emision") or ""
              
              try:
                total_comp = float(
                    fac.get("Total") or fac.get("Total_Comprobante") or 0.0
                )
              except:
                total_comp = 0.0

              fecha_vence = (
                  fac.get("F_Vence") or fac.get("Fecha_Vencimiento") or ""
              )

              try:
                saldo_adeudado = float(
                    fac.get("Saldo") or fac.get("Saldo_Adeudado") or 0.0
                )
              except:
                saldo_adeudado = 0.0

              if isinstance(fecha_emision, datetime):
                fecha_emision = fecha_emision.strftime("%Y-%m-%d")
              if isinstance(fecha_vence, datetime):
                fecha_vence = fecha_vence.strftime("%Y-%m-%d")

              item_factura = ft.Card(
                  content=ft.Container(
                      content=ft.Column(
                          [
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"Comp: {nro_comprobante}",
                                          size=13,
                                          weight=ft.FontWeight.BOLD,
                                          color=ft.Colors.BLUE_700,
                                      ),
                                      ft.Text(
                                          f"Saldo: S/ {saldo_adeudado:,.2f}",
                                          size=13,
                                          weight=ft.FontWeight.BOLD,
                                          color=ft.Colors.RED_400,
                                      ),
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"F. Emisión: {fecha_emision}",
                                          size=11,
                                          color=ft.Colors.GREY_700,
                                      ),
                                      ft.Text(
                                          f"F. Vence: {fecha_vence}",
                                          size=11,
                                          color=ft.Colors.GREY_700,
                                      ),
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                              ft.Text(
                                  f"Total Comprobante: S/ {total_comp:,.2f}",
                                  size=11,
                                  color=ft.Colors.BLACK,
                              ),
                          ],
                          spacing=3,
                      ),
                      padding=10,
                  )
              )
              lista_facturas.controls.append(item_factura)
          else:
            lista_facturas.controls.append(
                ft.Text(
                    "No se encontraron facturas adeudadas para este cliente.",
                    text_align=ft.TextAlign.CENTER,
                )
            )
        else:
          try:
            err_data = response.json().get("error", "Error desconocido")
          except:
            err_data = f"Código HTTP {response.status_code}"
          lista_facturas.controls.append(
              ft.Text(f"Error del servidor: {err_data}", color=ft.Colors.RED_400)
          )

        columna_resultados.controls.clear()
        columna_resultados.horizontal_alignment = ft.CrossAxisAlignment.START
        columna_resultados.controls.append(lista_facturas)
        page.update()

      except Exception as ex:
        columna_resultados.controls.clear()
        columna_resultados.controls.append(
            ft.Text(f"Error de conexión: {str(ex)}", color=ft.Colors.RED_400)
        )
        page.update()

    page.run_task(ejecutar_carga_detalle)

  # ==================== PANTALLA DE HOJA DE RUTA ====================
  def cargar_hoja_ruta_view():
    page.clean()
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    txt_titulo = ft.Text(
        f"👤 {usuario_actual.get('nombres_perso', 'Usuario')}",
        size=16,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
    )

    def volver_menu(e):
      mostrar_menu_principal()

    appbar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.WHITE,
                    on_click=volver_menu,
                    tooltip="Volver al Menú",
                ),
                txt_titulo,
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.Colors.BLUE_700,
        padding=15,
        border_radius=ft.border_radius.only(
            bottom_left=20, bottom_right=20
        ),
        width=400,
    )

    lista_clientes = ft.ListView(expand=1, spacing=10, padding=10)

    def obtener_datos(e=None):
      lista_clientes.controls.clear()
      lista_clientes.controls.append(
          ft.Row(
              [ft.ProgressRing()],
              alignment=ft.MainAxisAlignment.CENTER,
          )
      )
      page.update()

      hoy = datetime.now().strftime("%Y-%m-%d")
      id_persona = usuario_actual.get("id_persona")

      try:
        response = requests.get(
            f"{API_BASE_URL}/api/hoja_ruta",
            params={"fecha": hoy, "id_persona": str(id_persona)},
            timeout=10,
        )

        lista_clientes.controls.clear()

        if response.status_code == 200:
          resultados = response.json()
          if resultados and isinstance(resultados, list):
            for index, cli in enumerate(resultados):
              id_cliente = (
                  cli.get("id_cliente")
                  or cli.get("Id_Cliente")
                  or cli.get("ID_CLIENTE")
                  or cli.get("idCliente")
                  or cli.get("id_persona")
                  or cli.get("IdCliente")
              )

              ruc = cli.get("RUC") or cli.get("ruc") or ""
              nombre = (
                  cli.get("Razon_Social")
                  or cli.get("razon_social")
                  or cli.get("nombre")
                  or cli.get("nombres")
                  or cli.get("nombre_cliente")
                  or "Cliente sin nombre"
              )
              direccion = (
                  cli.get("Direccion")
                  or cli.get("direccion")
                  or cli.get("domicilio")
                  or "Sin dirección registrada"
              )

              cant_facturas = (
                  cli.get("Cantidad_Facturas")
                  or cli.get("cantidad_facturas")
                  or cli.get("Cant_Facturas")
                  or 0
              )
              try:
                cant_facturas = int(cant_facturas)
              except:
                cant_facturas = 0

              try:
                total_adeudado = float(
                    cli.get("Total_Adeudado")
                    or cli.get("total_adeudado")
                    or cli.get("TotalAdeudado")
                    or 0.0
                )
              except:
                total_adeudado = 0.0

              tiene_facturas = cant_facturas > 0

              def crear_click_handler(ic, rs):
                return lambda e: mostrar_detalle_deuda(ic, rs)

              btn_ver_detalle = ft.ElevatedButton(
                  text="Ver Detalle",
                  color=ft.Colors.WHITE if tiene_facturas else ft.Colors.GREY,
                  bgcolor=ft.Colors.BLUE_700
                  if tiene_facturas
                  else ft.Colors.GREY_300,
                  disabled=not tiene_facturas,
                  on_click=crear_click_handler(id_cliente, nombre),
              )

              tarjeta = ft.Card(
                  content=ft.Container(
                      content=ft.Column(
                          [
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"#{index + 1} - RUC: {ruc}",
                                          size=12,
                                          color=ft.Colors.BLUE_600,
                                          weight=ft.FontWeight.BOLD,
                                      ),
                                      ft.Text(
                                          f"Facturas: {cant_facturas}",
                                          size=12,
                                          color=ft.Colors.ORANGE_800
                                          if tiene_facturas
                                          else ft.Colors.GREY,
                                          weight=ft.FontWeight.BOLD,
                                      ),
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                              ft.Text(
                                  nombre,
                                  size=15,
                                  weight=ft.FontWeight.BOLD,
                              ),
                              ft.Row(
                                  [
                                      ft.Icon(
                                          ft.Icons.LOCATION_ON,
                                          size=14,
                                          color=ft.Colors.RED_400,
                                      ),
                                      ft.Text(
                                          direccion,
                                          size=13,
                                          color=ft.Colors.GREY_700,
                                          expand=True,
                                      ),
                                  ],
                                  spacing=5,
                              ),
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"Total: S/ {total_adeudado:,.2f}",
                                          size=14,
                                          color=ft.Colors.RED_400
                                          if tiene_facturas
                                          else ft.Colors.GREY,
                                          weight=ft.FontWeight.BOLD,
                                      ),
                                      btn_ver_detalle,
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                          ],
                          spacing=5,
                      ),
                      padding=15,
                  )
              )
              lista_clientes.controls.append(tarjeta)
          else:
            lista_clientes.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No hay clientes asignados para hoy.",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=30,
                )
            )
        else:
          error_msg = response.json().get(
              "error", "Error al consultar la API"
          )
          lista_clientes.controls.append(
              ft.Text(f"Error: {error_msg}", color=ft.Colors.RED_400)
          )

      except Exception as ex:
        lista_clientes.controls.clear()
        lista_clientes.controls.append(
            ft.Text(f"Error de conexión con la API: {str(ex)}", color=ft.Colors.RED_400)
        )

      page.update()

    btn_actualizar = ft.FloatingActionButton(
        icon=ft.Icons.REFRESH,
        on_click=obtener_datos,
        bgcolor=ft.Colors.BLUE_700,
        foreground_color=ft.Colors.WHITE,
    )

    contenedor_lista = ft.Container(
        content=lista_clientes, expand=True, width=380
    )

    page.add(
        appbar,
        ft.Container(height=10),
        ft.Row(
            [
                ft.Text(
                    "Clientes Asignados Hoy",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.GREY_700,
                ),
                ft.IconButton(
                    icon=ft.Icons.AUTORENEW, on_click=obtener_datos
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=380,
        ),
        contenedor_lista,
    )
    page.floating_action_button = btn_actualizar
    page.update()
    obtener_datos()

  # ==================== PANTALLA DE REGISTRO DE PEDIDOS ====================
  def cargar_registro_pedidos_view(e=None):
    page.clean()
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    def volver_menu(e):
      mostrar_menu_principal()

    appbar = ft.Container(
        content=ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.WHITE,
                    on_click=volver_menu,
                    tooltip="Volver al Menú",
                ),
                ft.Text(
                    "Toma de Pedido",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.WHITE,
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
        ),
        bgcolor=ft.Colors.GREEN_700,
        padding=15,
        border_radius=ft.border_radius.only(
            bottom_left=20, bottom_right=20
        ),
        width=400,
    )

    txt_ruc = ft.TextField(
        label="Ingrese RUC del Cliente", width=220, border_radius=10
    )
    lbl_cliente_info = ft.Text(
        "Cliente no seleccionado",
        size=13,
        color=ft.Colors.GREY_700,
        weight=ft.FontWeight.BOLD,
    )

    txt_articulo = ft.TextField(
        label="Buscar artículo por nombre...",
        width=320,
        border_radius=10,
        disabled=True,
    )
    lista_articulos = ft.ListView(expand=1, spacing=8, padding=5)

    lista_carrito = ft.ListView(expand=1, spacing=5, padding=5)
    lbl_total_carrito = ft.Text(
        "Total: S/ 0.00", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700
    )

    def actualizar_vista_carrito():
      lista_carrito.controls.clear()
      total_general = 0.0
      if pedido_actual["items"]:
        for idx, item in enumerate(pedido_actual["items"]):
          subtotal = item["cantidad"] * item["precio"]
          total_general += subtotal

          def crear_eliminar(i):
            return lambda e: (
                pedido_actual["items"].pop(i),
                actualizar_vista_carrito(),
            )

          tarjeta_cart = ft.Card(
              content=ft.Container(
                  content=ft.Column(
                      [
                          ft.Row(
                              [
                                  ft.Text(
                                      f"{item['nombre']}",
                                      size=12,
                                      weight=ft.FontWeight.BOLD,
                                      expand=True,
                                  ),
                                  ft.IconButton(
                                      icon=ft.Icons.DELETE,
                                      icon_color=ft.Colors.RED_400,
                                      icon_size=16,
                                      on_click=crear_eliminar(idx),
                                  ),
                              ],
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                          ),
                          ft.Row(
                              [
                                  ft.Text(
                                      f"Cant: {item['cantidad']} x S/ {item['precio']:,.2f}",
                                      size=11,
                                      color=ft.Colors.GREY_700,
                                  ),
                                  ft.Text(
                                      f"Subtotal: S/ {subtotal:,.2f}",
                                      size=11,
                                      weight=ft.FontWeight.BOLD,
                                      color=ft.Colors.BLACK,
                                  ),
                              ],
                              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                          ),
                      ],
                      spacing=2,
                  ),
                  padding=8,
              )
          )
          lista_carrito.controls.append(tarjeta_cart)
      else:
        lista_carrito.controls.append(
            ft.Text(
                "El carrito está vacío.",
                size=12,
                color=ft.Colors.GREY_700,
                text_align=ft.TextAlign.CENTER,
            )
        )

      lbl_total_carrito.value = f"Total General: S/ {total_general:,.2f}"
      page.update()

    def abrir_carrito(e):
      def cerrar_dlg_cart(e):
        dlg_carrito.open = False
        page.update()

      dlg_carrito = ft.AlertDialog(
          title=ft.Text(
              "🛒 Carrito de Compras", size=16, weight=ft.FontWeight.BOLD
          ),
          content=ft.Container(
              content=ft.Column(
                  [
                      lista_carrito,
                      ft.Divider(),
                      lbl_total_carrito,
                      ft.ElevatedButton(
                          text="Confirmar y Enviar Pedido",
                          bgcolor=ft.Colors.GREEN_700,
                          color=ft.Colors.WHITE,
                          width=300,
                      ),
                  ],
                  spacing=10,
              ),
              width=380,
              height=380,
          ),
          actions=[ft.TextButton("Cerrar", on_click=cerrar_dlg_cart)],
      )
      page.overlay.append(dlg_carrito)
      dlg_carrito.open = True
      actualizar_vista_carrito()

    btn_ver_carrito = ft.IconButton(
        icon=ft.Icons.SHOPPING_CART,
        icon_color=ft.Colors.WHITE,
        tooltip="Ver Carrito",
        on_click=abrir_carrito,
    )

    # Validación de RUC conectada correctamente a la API Flask
    def buscar_cliente(e):
      ruc_val = txt_ruc.value.strip() if txt_ruc.value else ""
      print(f"DEBUG: Intentando validar RUC -> {ruc_val}")  # Saldrá en tu consola

      if not ruc_val:
        mostrar_alerta("Ingrese un RUC válido")
        return

      try:
        response = requests.get(
            f"{API_BASE_URL}/api/cliente/buscar",
            params={"ruc": ruc_val},
            timeout=10,
        )

        print(
            f"DEBUG: Código de respuesta API Cliente: {response.status_code}"
        )

        if response.status_code == 200:
          res = response.json()
          print(f"DEBUG: Datos recibidos del cliente: {res}")

          if res:
            pedido_actual["id_cliente"] = (
                res.get("id_cliente")
                or res.get("Id_Cliente")
                or res.get("ID_CLIENTE")
            )
            pedido_actual["razon_social"] = (
                res.get("Razon_Social")
                or res.get("razon_social")
                or res.get("nombre")
                or "Sin nombre"
            )
            pedido_actual["ruc"] = ruc_val

            lbl_cliente_info.value = f"Cliente: {pedido_actual['razon_social']}"
            lbl_cliente_info.color = ft.Colors.GREEN_700
            txt_articulo.disabled = False
            mostrar_alerta(
                f"Cliente encontrado: {pedido_actual['razon_social']}",
                es_error=False,
            )
          else:
            lbl_cliente_info.value = "Cliente no encontrado"
            lbl_cliente_info.color = ft.Colors.RED_400
            txt_articulo.disabled = True
            mostrar_alerta("No se encontró ningún cliente con ese RUC")
        else:
          mostrar_alerta("Error al consultar el cliente en la API")
        page.update()
      except Exception as ex:
        print(f"DEBUG EXCEPTION: {str(ex)}")
        mostrar_alerta(f"Error de conexión: {str(ex)}")

    btn_buscar_ruc = ft.ElevatedButton(
        text="Validar RUC",
        bgcolor=ft.Colors.GREEN_700,
        color=ft.Colors.WHITE,
        height=45,
        on_click=buscar_cliente,  # <-- Vinculado correctamente aquí
    )
    
    def buscar_articulos(e):
      filtro = txt_articulo.value.strip() if txt_articulo.value else ""
      if len(filtro) < 2:
        lista_articulos.controls.clear()
        lista_articulos.controls.append(
            ft.Text(
                "Escriba al menos 2 caracteres para buscar...",
                color=ft.Colors.GREY_700,
                text_align=ft.TextAlign.CENTER,
            )
        )
        page.update()
        return

      try:
        response = requests.get(
            f"{API_BASE_URL}/api/articulos/buscar",
            params={"txtNombre": filtro},
            timeout=10,
        )

        lista_articulos.controls.clear()

        if response.status_code == 200:
          articulos = response.json()
          if articulos and isinstance(articulos, list):
            for art in articulos:
              cod_art = (
                  art.get("cod_articulo")
                  or art.get("Cod_Articulo")
                  or art.get("codigo")
              )
              nombre_comercial = (
                  art.get("Nombre_Comercial")
                  or art.get("nombre_comercial")
                  or art.get("Nombre")
                  or "Artículo sin nombre"
              )
              generico = art.get("Generico") or art.get("generico") or ""
              laboratorio = art.get("Laboratorio") or art.get("laboratorio") or ""
              presentacion = (
                  art.get("Presentacion")
                  or art.get("presentacion")
                  or art.get("Presentación")
                  or "N/D"
              )
              stock = art.get("Stock") or art.get("stock") or 0
              
              # PROTECCIÓN DE PRECIO (Evita el error Unknown format code 'f')
              try:
                precio = float(
                    art.get("Precio_Venta") or art.get("precio_venta") or 0.0
                )
              except:
                precio = 0.0

              txt_cant = ft.TextField(
                  value="1",
                  width=60,
                  height=35,
                  text_align=ft.TextAlign.CENTER,
                  text_size=12,
              )

              def agregar_al_carrito(c_art, n_art, p_art, t_c):
                def click_agregar(e):
                  try:
                    cantidad = int(t_c.value)
                    if cantidad <= 0:
                      raise ValueError()
                  except:
                    mostrar_alerta("Ingrese una cantidad válida")
                    return

                  pedido_actual["items"].append({
                      "cod_articulo": c_art,
                      "nombre": n_art,
                      "precio": float(p_art),
                      "cantidad": cantidad,
                  })
                  mostrar_alerta(
                      f"Agregado al carrito: {n_art} ({cantidad})",
                      es_error=False,
                  )

                return click_agregar

              btn_agregar = ft.ElevatedButton(
                  text="Agregar",
                  bgcolor=ft.Colors.BLUE_700,
                  color=ft.Colors.WHITE,
                  height=35,
                  on_click=agregar_al_carrito(
                      cod_art, nombre_comercial, precio, txt_cant
                  ),
              )

              tarjeta_art = ft.Card(
                  content=ft.Container(
                      content=ft.Column(
                          [
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"{nombre_comercial}",
                                          size=13,
                                          weight=ft.FontWeight.BOLD,
                                          color=ft.Colors.BLUE_700,
                                          expand=True,
                                      ),
                                      ft.Text(
                                          f"Stock: {stock}",
                                          size=11,
                                          color=ft.Colors.ORANGE_800,
                                          weight=ft.FontWeight.BOLD,
                                      ),
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                              ft.Text(
                                  f"Presentación: {presentacion} | Genérico: {generico}",
                                  size=11,
                                  color=ft.Colors.GREY_700,
                              ),
                              ft.Text(
                                  f"Laboratorio: {laboratorio}",
                                  size=11,
                                  color=ft.Colors.GREY_700,
                              ),
                              ft.Row(
                                  [
                                      ft.Text(
                                          f"Precio: S/ {precio:,.2f}",
                                          size=12,
                                          weight=ft.FontWeight.BOLD,
                                          color=ft.Colors.BLACK,
                                      ),
                                      ft.Row(
                                          [
                                              ft.Text("Cant:", size=11),
                                              txt_cant,
                                              btn_agregar,
                                          ],
                                          spacing=5,
                                      ),
                                  ],
                                  alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                              ),
                          ],
                          spacing=4,
                      ),
                      padding=10,
                  )
              )
              lista_articulos.controls.append(tarjeta_art)
          else:
            lista_articulos.controls.append(
                ft.Text(
                    "No se encontraron artículos con ese nombre.",
                    color=ft.Colors.GREY_700,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        else:
          lista_articulos.controls.append(
              ft.Text("Error al buscar artículos", color=ft.Colors.RED_400)
          )
        page.update()
      except Exception as ex:
        lista_articulos.controls.clear()
        lista_articulos.controls.append(
            ft.Text(f"Error de conexión: {str(ex)}", color=ft.Colors.RED_400)
        )
        page.update()

    txt_articulo.on_change = buscar_articulos

    appbar.content.controls.insert(2, btn_ver_carrito)

    contenedor_form = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Selección de Cliente",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Row(
                    [txt_ruc, btn_buscar_ruc],
                    spacing=10,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                lbl_cliente_info,
                ft.Divider(height=15),
                ft.Text(
                    "Búsqueda de Artículos",
                    size=15,
                    weight=ft.FontWeight.BOLD,
                ),
                txt_articulo,
                ft.Divider(height=10),
                lista_articulos,
            ],
            spacing=10,
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
        width=380,
    )

    page.add(appbar, ft.Container(height=5), contenedor_form)
    page.floating_action_button = None
    page.update()

  # ==================== PANTALLA DE MENÚ PRINCIPAL ====================
  def mostrar_menu_principal():
    page.clean()
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.floating_action_button = None

    nombre_usuario = usuario_actual.get("nombres_perso", "Usuario")

    def cerrar_sesion(e):
      usuario_actual.clear()
      mostrar_login()

    btn_hoja_ruta = ft.ElevatedButton(
        text="Hoja de Ruta / Clientes",
        icon=ft.Icons.MAP,
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE
        ),
        on_click=lambda e: cargar_hoja_ruta_view(),
    )

    btn_nuevo_pedido = ft.ElevatedButton(
        text="Registrar Pedido",
        icon=ft.Icons.ADD_SHOPPING_CART,
        width=300,
        height=50,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREEN_700, color=ft.Colors.WHITE
        ),
        on_click=cargar_registro_pedidos_view,
    )

    btn_salir = ft.OutlinedButton(
        text="Cerrar Sesión",
        icon=ft.Icons.LOGOUT,
        width=300,
        height=45,
        style=ft.ButtonStyle(color=ft.Colors.RED_400),
        on_click=cerrar_sesion,
    )

    tarjeta_menu = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.DASHBOARD, size=50, color=ft.Colors.BLUE_700
                    ),
                    ft.Text(
                        "Menú Principal",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"Bienvenido, {nombre_usuario}",
                        size=13,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=20),
                    btn_hoja_ruta,
                    btn_nuevo_pedido,
                    ft.Container(height=5),
                    btn_salir,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=30,
            width=360,
        )
    )

    page.add(tarjeta_menu)
    page.update()

  # ==================== PANTALLA DE LOGIN ====================
  def mostrar_login():
    page.clean()
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.floating_action_button = None

    txt_usuario = ft.TextField(
        label="Usuario / Código",
        prefix_icon=ft.Icons.PERSON,
        border_radius=10,
    )
    txt_clave = ft.TextField(
        label="Contraseña",
        password=True,
        can_reveal_password=True,
        prefix_icon=ft.Icons.LOCK,
        border_radius=10,
    )

    btn_ingresar = ft.ElevatedButton(
        text="INGRESAR",
        width=300,
        height=45,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_700, color=ft.Colors.WHITE
        ),
    )

    def ejecutar_login(e):
      usuario = txt_usuario.value.strip() if txt_usuario.value else ""
      clave = txt_clave.value.strip() if txt_clave.value else ""

      if not usuario or not clave:
        mostrar_alerta("Ingrese usuario y contraseña")
        return

      try:
        response = requests.post(
            f"{API_BASE_URL}/api/login",
            json={"usuario": usuario, "clave": clave},
            timeout=10,
        )

        if response.status_code == 200:
          resultado = response.json()
          usuario_actual.clear()
          usuario_actual.update(resultado)
          mostrar_menu_principal()
        else:
          try:
            error_msg = response.json().get("error", "Credenciales incorrectas")
          except:
            error_msg = "Credenciales incorrectas"
          mostrar_alerta(error_msg)

      except Exception as ex:
        mostrar_alerta(f"Error de conexión: {str(ex)}")

    btn_ingresar.on_click = ejecutar_login

    tarjeta_login = ft.Card(
        content=ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.LOCAL_SHIPPING,
                        size=60,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Text(
                        "Pedidos Droguería",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Inicie sesión para continuar",
                        size=12,
                        color=ft.Colors.GREY_700,
                    ),
                    ft.Divider(height=20),
                    txt_usuario,
                    txt_clave,
                    ft.Container(height=10),
                    btn_ingresar,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15,
            ),
            padding=30,
            width=360,
        )
    )

    page.add(tarjeta_login)
    page.update()

def main(page: ft.Page):
   # Todo tu código de la interfaz y lógica aquí...
   page.title = "App Pedidos Drogueria"
   mostrar_login(page)
  

# FORMA CORRECTA Y ACTUAL DE LLAMAR A FLET:
if __name__ == "__main__":
  ft.app(target=main)
