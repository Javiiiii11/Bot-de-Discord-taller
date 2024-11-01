import asyncio
import requests
import io
import discord
import random

from discord.ext import commands
from PIL import Image
from datetime import datetime
#%% Variables y creacion del bot
API_URL = 'http://localhost:5000/motos'
API_URL_IMAGENES = "https://api.unsplash.com/photos/random?query=motorcycle&orientation=landscape&client_id=C93wup_gJl0idxggB79Qlv8Er4jlEfTcn-akJZaayUU"
contraseña_mecanico = 'mecanico123'
admin_Taller = False
admin_Ventas = False
contraseña_admin_taller = "taller123"
contraseña_admin_ventas = "ventas123"
contraseña_rol_admin = "aprobado"

# Crear el bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents) # Prefijo de comandos

#%% Métodos imagenes
@bot.command(name='imagen')
async def generar_imagen_moto(ctx):
    await ctx.send("Mostrando 1 foto de la galería...")

    try:
        data = requests.get(API_URL_IMAGENES).json()
        img_data = requests.get(data["urls"]["regular"]).content

        # Abre la imagen y guárdala en un objeto BytesIO
        image = Image.open(io.BytesIO(img_data))
        with io.BytesIO() as image_binary:
            image.save(image_binary, 'PNG')
            image_binary.seek(0)
            await ctx.send(file=discord.File(fp=image_binary, filename='motorcycle.png'))

    except requests.exceptions.RequestException as e:
        await ctx.send("Error al generar la imagen.")

#%% Métodos

@bot.event
async def on_ready():
    print(f"Bot iniciado como:  {bot.user}")

@bot.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        return
    await bot.process_commands(message)

@bot.command(name='contraseñas')
async def contraseñas(ctx):
    message = await ctx.send(f"**Contraseña de admin taller:** {contraseña_admin_taller}\n**Contraseña de admin ventas:** {contraseña_admin_ventas}\n**Contraseña de rol admin:** {contraseña_rol_admin}\n\nLas contraseñas se eliminarán en 10 segundos.")
    await asyncio.sleep(10)
    await message.delete()

@bot.command(name='user_info')
async def user_info(ctx):
    """Displays information about the user who invoked the command."""
    user = ctx.author
    roles = ', '.join([role.name for role in user.roles if role.name != "@everyone"])
    if not roles:
        roles = "Sin roles"
    user_info_msg = (
        f"**Mi Information:**\n"
        f"**Username:** {user.name}\n"
        f"**ID:** {user.id}\n"
        f"**Top Role:** {user.top_role}\n"
        f"**Roles:** {roles}\n"
        f"**Status:** {user.status}\n"
        f"**Avatar URL:** {user.avatar.with_size(256).url}\n"
    )
    await ctx.send(user_info_msg)

@bot.command(name='admin')
async def admin(ctx):
    """Asigna el rol de 'admin' al usuario que invocó el comando, si proporciona la contraseña correcta."""
    role_name = "admin"
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role in ctx.author.roles:
        await ctx.send("Ya eres admin.")
        return

    await ctx.send("Introduce la contraseña de administrador:")

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        if msg.content != contraseña_rol_admin:
            await ctx.send("Contraseña incorrecta.")
            return
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir la contraseña!')
        return

    try:
        await ctx.author.add_roles(role)
        await ctx.send(f"Rol '{role_name}' se te ha asignado.")
    except discord.Forbidden:
        await ctx.send("No tengo permisos para asignar roles.")
    except discord.HTTPException as e:
        await ctx.send(f"Fallo al asignar el rol.")

@bot.command(name='apagar')
@commands.has_permissions(administrator=True)
async def apagar(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Apagando el bot...", delete_after=2)
    await bot.close()

@bot.command(name='ayuda')
async def ayuda(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    help_msg = (
        "**Lista de comandos:**\n"
        "1. **/contraseñas**: Te muestra las contraseñas\n"
        "2. **/registro**: Te tienes que registrar para poder usar el bot\n"
        "3. **/admin**: Te el rol de 'admin', (necesario para algunos comandos).\n"
        "4. **/menu**: Muestra un menú con varias opciones.\n"
        "5. **/imagen**: Genera y muestra una imagen.\n"
        "6. **/user_info**: Muestra información tu usuario.\n"
        "4. **/apagar**: Apaga el bot.\n"
    )
    await ctx.send(help_msg)

@bot.command(name='cls')
@commands.has_permissions(manage_messages=True)
async def limpiar_chat(ctx, limit: int = 10000): # Por defecto, se eliminarán 1000 mensajes

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    """Limpia el chat eliminando mensajes en masa."""
    try:
        await ctx.channel.purge(limit=limit) # Elimina los mensajes
    except discord.Forbidden:
        await ctx.send("No tengo permisos para eliminar mensajes.")
    except discord.HTTPException as e:
        await ctx.send(f"Error al eliminar mensajes")

@bot.command(name='registro')
async def registro(ctx):
    """Verifies the user and assigns the 'autorizado' role."""
    role_name = "autorizado"
    role = discord.utils.get(ctx.guild.roles, name=role_name)

    if role in ctx.author.roles:
        await ctx.send("Ya estas registrado.")
        return

    # Generate a random number for verification
    num = random.randint(1000, 9999)
    await ctx.send(f"Por favor, verifica tu cuenta. Te he enviado un mensaje privado con un número. Introduce el número aquí: ")
    await ctx.author.send(f"Número: {num}.")

    try:
        msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        if msg.content != str(num):
            await ctx.send("Verificación fallida.")
            return
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para verificar!')
        return

    try:
        await ctx.author.add_roles(role)
        await ctx.send(f"Registro completado")
    except discord.HTTPException as e:
        await ctx.send(f"Fallo al asignar el rol")

#%% Métodos taller
@bot.command(name='listar_motos_taller')
async def listar_motos_taller(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    """Lista todas las motos que están en el taller."""
    await ctx.send("Listando motos...", delete_after=1)
    try:
        response = requests.get(f"{API_URL}/taller")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        motos = response.json()  # Suponiendo que la respuesta es JSON

        if not motos:
            await ctx.send("No hay motos disponibles.")
            return

        motos_msg = "***Lista de Motos:***\n\n"
        for moto in motos:
            motos_msg += f"**ID:** {moto['id']}, **Marca:** {moto['marca']}, **Modelo:** {moto['modelo']}, **Año:** {moto['año']}, **Estado:** {moto['estado']}\n"
        await ctx.send(motos_msg)
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al obtener las motos.")

@bot.command(name='llevar_moto_taller')
async def llevar_moto_taller(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Introduce la marca de la moto:")
    try:
        marca_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        marca = marca_msg.content

        await ctx.send("Introduce el modelo de la moto:")
        modelo_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        modelo = modelo_msg.content

        await ctx.send("Introduce el año de la moto:")
        try:
            año_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
            año = int(año_msg.content)
            current_year = datetime.now().year
            if not (1900 <= año <= current_year):
                await ctx.send(f"El año introducido ({año}) no es válido. Debe ser menor o igual al año actual ({current_year}) y mayor de 1900.")
                return
        except ValueError:
            await ctx.send("Por favor, introduce un año válido.")
            return

        await ctx.send("Describe el problema de la moto:")
        estado_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        estado = estado_msg.content

        await ctx.send(f"Has introducido:\nMarca: {marca}\nModelo: {modelo}\nAño: {año}\nProblema: {estado}")
        confirmation_message = await ctx.send("¿Es correcto?")
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.send("¡Vuelve a intentarlo!")
                return
        except asyncio.TimeoutError:
            await ctx.send('¡Tiempo agotado para confirmar los datos!')
            return

        await ctx.send("Llevando moto al taller...", delete_after=1)

        response = requests.post(f"{API_URL}/taller", json={"marca": marca, "modelo": modelo, "año": año, "estado": estado})
        if response.status_code == 201:
            id_moto = response.json().get('id')
            await ctx.send(f"Moto llevada al taller exitosamente con el ID: {id_moto}")
        else:
            await ctx.send(f"Error al llevar la moto al taller.")

    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir los datos de la moto!')
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comunicarse con la API.")

@bot.command(name='cambiar_estado')
async def cambiar_estado(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Introduce el ID de la moto para cambiar su estado:")
    try:
        id_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        id_moto = id_msg.content

        await ctx.send("Introduce el nuevo estado de la moto:")
        estado_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        estado = estado_msg.content

        await ctx.send(f"Has introducido:\nID: {id_moto}\nNuevo estado: {estado}")
        confirmation_message = await ctx.send("¿Es correcto?")
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.send("¡Vuelve a intentarlo!")
                return
        except asyncio.TimeoutError:
            await ctx.send('¡Tiempo agotado para confirmar los datos!')
            return

        await ctx.send("Cambiando estado de la moto...", delete_after=1)

        response = requests.put(f"{API_URL}/taller/{id_moto}", json={"estado": estado})
        if response.status_code == 200:
            await ctx.send("Estado de la moto cambiado exitosamente.\n")
        else:
            await ctx.send(f"Error al cambiar el estado de la moto.")

    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir los datos de la moto!')
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comunicarse con la API.")

@bot.command(name='ver_estado_1_moto')
async def ver_estado_1_moto(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    try:
        # Pedir el ID de la moto
        await ctx.send("Introduce el ID de la moto que deseas ver:")
        id_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        id_moto = id_msg.content
        await ctx.send("Buscando la moto...", delete_after=1)

        # Obtener la moto con el ID especificado
        response = requests.get(f"{API_URL}/taller/{id_moto}")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        moto = response.json()  # Suponiendo que la respuesta es JSON

        # Mostrar la información de la moto
        if not moto:
            await ctx.send("No se encontró la moto.")
            return

        moto_msg = f"**ID:** {moto['id']}, **Marca:** {moto['marca']}, **Modelo:** {moto['modelo']}, **Año:** {moto['año']}, **Estado:** {moto['estado']}"
        await ctx.send(moto_msg)
    except requests.exceptions.RequestException as e:
        await ctx.send(f"No se encontró la moto con el ID especificado.")

@bot.command(name='eliminar_moto_taller')
async def eliminar_moto_taller(ctx, id_moto):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    try:
        await ctx.send("Buscando la moto...", delete_after=1)

        response = requests.get(f"{API_URL}/taller/{id_moto}")
        response.raise_for_status()
        moto = response.json()

        if not moto:
            await ctx.send("Error, no se encontró la moto")
            return

        response = requests.delete(f"{API_URL}/taller/{id_moto}")
        response.raise_for_status()

        await ctx.send("Operación realizada correctamente")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al buscar la moto.")

@bot.command(neme = 'recoger_moto_taller')
async def recoger_moto_taller(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    try:
        await ctx.send("Introduce el ID de la moto para recogerla:")
        id_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        id_moto = id_msg.content

        await ctx.send("Recogiendo moto...", delete_after=1)
        await eliminar_moto_taller(ctx, id_moto)

    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al recoger la moto.")

#%% Métodos Ventas

@bot.command(name='comprar_moto_nueva')
async def comprar_moto_nueva(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        await ctx.send("No tienes permisos para usar este comando.")
        return

    await ctx.send("Introduce el ID de la moto que deseas comprar:")
    try:
        id_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        id_moto = id_msg.content

        await ctx.send("Comprando moto...", delete_after=1)

        response = requests.get(f"{API_URL}/nuevas/{id_moto}")
        response.raise_for_status()
        moto = response.json()

        if not moto:
            await ctx.send("Moto no encontrada.")
            return

        response = requests.delete(f"{API_URL}/nuevas/{id_moto}")
        response.raise_for_status()

        await ctx.send(f"Operación realizada correctamente")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comprar la moto.")


@bot.command(name='listar_motos_nuevas')
async def listar_motos_nuevas(ctx):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Listando motos...", delete_after=1)
    try:
        response = requests.get(f"{API_URL}/nuevas")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        motos = response.json()  # Suponiendo que la respuesta es JSON

        if not motos:
            await ctx.send("No hay motos disponibles.")
            return

        motos_msg = "***Lista de Motos:***\n\n"
        for moto in motos:
            motos_msg += f"**ID:** {moto['id']}, **Marca:** {moto['marca']}, **Modelo:** {moto['modelo']}, **Año:** {moto['año']}\n"
        await ctx.send(motos_msg)
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al obtener las motos.")

@bot.command(name='eliminar_moto_nueva')
async def eliminar_moto_nueva(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    try:
        # Introducir el ID de la moto
        await ctx.send("Introduce el ID de la moto que deseas eliminar:")
        id_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        id_moto = id_msg.content  # Obtener el contenido del mensaje

        await ctx.send("Buscando la moto...", delete_after=1)

        response = requests.get(f"{API_URL}/nuevas/{id_moto}")
        response.raise_for_status()
        moto = response.json()

        if not moto:
            await ctx.send("Error, no se encontró la moto")
            return

        response = requests.delete(f"{API_URL}/nuevas/{id_moto}")
        response.raise_for_status()

        await ctx.send(f"Operación realizada correctamente")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al eliminar la moto.")

@bot.command(name='poner_moto_venta')
async def poner_moto_venta(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return
    await ctx.send("Introduce la marca de la moto:")
    try:
        marca_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        marca = marca_msg.content

        await ctx.send("Introduce el modelo de la moto:")
        modelo_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        modelo = modelo_msg.content

        await ctx.send("Introduce el año de la moto:")
        try:
            año_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
            año = int(año_msg.content)
            current_year = datetime.now().year
            if not (1900 <= año <= current_year):
                await ctx.send(f"El año introducido ({año}) no es válido. Debe ser menor o igual al año actual ({current_year}) y mayor de 1900.")
                return
        except ValueError:
            await ctx.send("Por favor, introduce un año válido, vuelve a intentarlo")
            return

        await ctx.send("Introduce el precio de la moto:")
        try:
            precio_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
            precio = float(precio_msg.content)
            if precio < 0:
                await ctx.send("El precio debe ser mayor que 0, vuelve a intentarlo")
                return
        except ValueError:
            await ctx.send("Por favor, introduce un precio válido, vuelve a intentarlo")
            return

        await ctx.send(f"Has introducido:\nMarca: {marca}\nModelo: {modelo}\nAño: {año}\nPrecio: {precio}")
        confirmation_message = await ctx.send("¿Es correcto?")
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.send("¡Vuelve a intentarlo!")
                return
        except asyncio.TimeoutError:
            await ctx.send('¡Tiempo agotado para confirmar los datos!')
            return

        await ctx.send("Poniendo moto a la venta...", delete_after=1)

        response = requests.post(f"{API_URL}/nuevas", json={
            "marca": marca,
            "modelo": modelo,
            "año": año,
            "precio": precio,
        })
        if response.status_code == 201:
            await ctx.send("Moto puesta a la venta exitosamente.")
        else:
            await ctx.send("Error al poner la moto a la venta.")
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir los datos!')
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comunicarse con la API")

@bot.command(name='comprar_pieza')
async def comprar_pieza(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Introduce la referencia de la pieza que deseas comprar:")
    try:
        referencia_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        referencia = referencia_msg.content.upper()  # Convertir a mayúsculas

        if not referencia:
            await ctx.send("Referencia no válida.")
            return
        await ctx.send("Comprando pieza...", delete_after=1)

        # Obtener la pieza
        response = requests.get(f"{API_URL}/piezas/{referencia}")
        response.raise_for_status()
        pieza = response.json()

        if not pieza:
            await ctx.send("Pieza no encontrada.")
            return
        if not pieza['disponible']:
            await ctx.send("La pieza no está disponible.")
            return
        if pieza['cantidad'] <= 0:
            await ctx.send("No quedan en stock.")
            return

        # Reducir la cantidad en 1
        nueva_cantidad = pieza['cantidad'] - 1
        disponible = nueva_cantidad > 0

        # Actualizar la pieza
        response = requests.put(f"{API_URL}/piezas/{referencia}", json={"cantidad": nueva_cantidad, "disponible": disponible})
        response.raise_for_status()

        await ctx.send(f"Operación realizada correctamente. Cantidades restante: {nueva_cantidad}")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comprar la pieza.")

@bot.command(name='listar_piezas')
async def listar_piezas(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Listando piezas...", delete_after=1)
    try:
        response = requests.get(f"{API_URL}/piezas")
        response.raise_for_status()  # Lanza un error si la solicitud falla
        piezas = response.json()  # Suponiendo que la respuesta es JSON

        if not piezas:
            await ctx.send("No hay piezas disponibles.")
            return

        piezas_msg = "***Lista de Piezas:***\n\n"
        for pieza in piezas:
            cantidad = pieza.get('cantidad', 'N/A')  # Use 'N/A' if 'cantidad' is not found
            disponible = pieza.get('disponible', 'N/A')  # Use 'N/A' if 'disponible' is not found
            if cantidad == 0:
                disponible = False
            pieza_info = f"**Referencia:** {pieza['referencia']}, **Nombre:** {pieza['nombre']}, **Cantidad:** {cantidad}, **Disponibilidad:** {disponible}\n"
            if len(piezas_msg) + len(pieza_info) > 2000:
                await ctx.send(piezas_msg)
                piezas_msg = ""
            piezas_msg += pieza_info

        if piezas_msg:
            await ctx.send(piezas_msg)
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al obtener las piezas.")

@bot.command(name='eliminar_pieza')
async def eliminar_pieza(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    try:
        # Introducir la referencia de la pieza
        await ctx.send("Introduce la referencia de la pieza que deseas eliminar:")
        referencia_borrar = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        referencia_borrar = referencia_borrar.content.upper()

        await ctx.send("Buscando la pieza...", delete_after=1)

        response = requests.get(f"{API_URL}/piezas/{referencia_borrar}")
        response.raise_for_status()
        pieza = response.json()

        if not pieza:
            await ctx.send("Error, no se encontró la pieza")
            return

        response = requests.delete(f"{API_URL}/piezas/{referencia_borrar}")
        response.raise_for_status()

        await ctx.send("Operación realizada correctamente")
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al eliminar la pieza.")

@bot.command(name='reponer_stock_piezas')
async def reponer_stock_piezas(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Introduce la referencia de la pieza que deseas reponer:")
    try:
        referencia_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        referencia = referencia_msg.content.upper()

        await ctx.send("Introduce la cantidad de piezas que deseas reponer:")
        try:
            cantidad_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
            cantidad = int(cantidad_msg.content)
            if cantidad <= 0:
                await ctx.send("La cantidad debe ser mayor que 0.")
                return
        except ValueError:
            await ctx.send("Por favor, introduce un número válido.")
            return

        # Obtener la pieza actual
        response = requests.get(f"{API_URL}/piezas/{referencia}")
        if response.status_code != 200:
            await ctx.send("Pieza no encontrada.")
            return
        pieza = response.json()
        cantidad_actual = pieza.get('cantidad', 0)

        # Sumar la cantidad nueva a la cantidad actual
        nueva_cantidad = cantidad_actual + cantidad

        # Confirmar los datos
        await ctx.send(f"Has introducido:\nReferencia: {referencia}\nCantidad actual: {cantidad_actual}\nCantidad a reponer: {cantidad}\nNueva cantidad: {nueva_cantidad}")
        confirmation_message = await ctx.send("¿Es correcto?")
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.send("¡Vuelve a intentarlo!")
                return
        except asyncio.TimeoutError:
            await ctx.send('¡Tiempo agotado para confirmar los datos!')
            return

        await ctx.send("Reponiendo stock de piezas...", delete_after=1)

        # Actualizar la cantidad y disponibilidad
        response = requests.put(f"{API_URL}/piezas/{referencia}", json={"cantidad": nueva_cantidad, "disponible": True})
        if response.status_code == 200:
            await ctx.send(f"Stock de la pieza repuesto exitosamente.")
        else:
            await ctx.send(f"Error al reponer el stock de piezas.")

    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir los datos de la pieza!')
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error al comunicarse con la API.")

@bot.command(name='poner_pieza_venta')
async def poner_pieza_venta(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    await ctx.send("Introduce la referencia de la pieza:")
    try:
        referencia_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        referencia = referencia_msg.content.upper()

        await ctx.send("Introduce el nombre de la pieza:")
        nombre_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
        nombre = nombre_msg.content

        await ctx.send("Introduce la cantidad de piezas:")
        try:
            cantidad_msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
            cantidad = int(cantidad_msg.content)
            if cantidad < 0:
                await ctx.send("La cantidad debe ser mayor o igual a 0.")
                return
        except ValueError:
            await ctx.send("Por favor, introduce un número válido.")
            return

        await ctx.send(f"Has introducido:\nReferencia: {referencia}\nNombre: {nombre}\nCantidad: {cantidad}")
        confirmation_message = await ctx.send("¿Es correcto?")
        await confirmation_message.add_reaction('✅')
        await confirmation_message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            if str(reaction.emoji) == '❌':
                await ctx.send("¡Vuelve a intentarlo!")
                return
            else:
                await ctx.send("Poniendo pieza a la venta...", delete_after=1)

                response = requests.post(f"{API_URL}/piezas", json={
                    "referencia": referencia,
                    "nombre": nombre,
                    "cantidad": cantidad,
                    "disponible": True
                })
                if response.status_code == 201:
                    await ctx.send("Pieza puesta a la venta exitosamente.")
                else:
                    await ctx.send("Error al poner la pieza a la venta.")
        except asyncio.TimeoutError:
            await ctx.send('¡Tiempo agotado para confirmar los datos!')
            return
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado para introducir los datos de la pieza!')

#%% Menú Inicio
@bot.command(name='menu')
async def menu(ctx):
    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    # Enviar el nuevo mensaje de menú
    menu_msg = "\nMenú:\n1. Apartado de ventas.\n2. Apartado de taller.\n3. Galería de imágenes. \n4. Mi información. \n5. Salir."
    menu_message = await ctx.send(menu_msg)

    # Añadir reacciones al nuevo mensaje de menú
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']
    for reaction in reactions:
        await menu_message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado!')
    else:
        if str(reaction.emoji) == '1️⃣':
            await menu_ventas(ctx)
        elif str(reaction.emoji) == '2️⃣':
            await menu_taller(ctx)
        elif str(reaction.emoji) == '3️⃣':
            await generar_imagen_moto(ctx)
            await menu(ctx)
        elif str(reaction.emoji) == '4️⃣':
            await user_info(ctx)
            await menu(ctx)
        elif str(reaction.emoji) == '5️⃣':
            await ctx.send("Hasta pronto, ¡adiós!")

#%%Menu ventas
async def menu_ventas(ctx, admin_Ventas=False):
    # Check if the user has the "autorizado" role
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    # Send the appropriate menu message based on the admin status
    if admin_Ventas:
        ventas_msg = (
            "Menú de ventas:\n"
            "1. Comprar moto.\n"
            "2. Comprar pieza.\n"
            "3. Ver todas las motos.\n"
            "4. Ver todas las piezas.\n"
            "5. Eliminar moto.\n"
            "6. Eliminar pieza.\n"
            "7. Poner moto a la venta.\n"
            "8. Poner pieza a la venta.\n"
            "9. Reponer stock de piezas.\n"
            "10. Cerrar sesión."
        )
    else:
        ventas_msg = (
            "Menú de ventas:\n"
            "1. Comprar moto.\n"
            "2. Comprar pieza.\n"
            "3. Ver todas las motos.\n"
            "4. Ver todas las piezas.\n"
            "5. Opciones administrador.\n"
            "6. Cerrar sesión."
        )

    ventas_message = await ctx.send(ventas_msg)

    # Add reactions for the menu options
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
    if admin_Ventas:
        reactions.extend(['7️⃣', '8️⃣', '9️⃣', '🔟'])


    for reaction in reactions:
        await ventas_message.add_reaction(reaction)

    def check(reaction, user):
        if admin_Ventas:
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        else:
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado!')
    else:
        if str(reaction.emoji) == '1️⃣':
            await comprar_moto_nueva(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '2️⃣':
            await comprar_pieza(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '3️⃣':
            await listar_motos_nuevas(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '4️⃣':
            await listar_piezas(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '5️⃣':
            if admin_Ventas:
                await eliminar_moto_nueva(ctx)
                await menu_ventas(ctx, admin_Ventas=admin_Ventas)
            else:
                await ctx.send("Introduce la contraseña de administrador:")
                try:
                    msg = await bot.wait_for('message', timeout=30.0, check=lambda message: message.author == ctx.author)
                    if msg.content == contraseña_admin_ventas:
                        await ctx.send("**Contraseña correcta**. Aquí tienes las opciones adicionales...")
                        await menu_ventas(ctx, admin_Ventas=True)
                    else:
                        await ctx.send("Contraseña incorrecta.")
                        await menu_ventas(ctx, admin_Ventas=False)
                except asyncio.TimeoutError:
                    await ctx.send('¡Tiempo agotado para introducir la contraseña de administrador!')
        elif str(reaction.emoji) == '6️⃣':
            if admin_Ventas:
                await eliminar_pieza(ctx)
                await menu_ventas(ctx, admin_Ventas=admin_Ventas)
            else:
                await ctx.send("Sesión cerrada.")
                await menu(ctx)
        elif str(reaction.emoji) == '7️⃣' and admin_Ventas:
            await poner_moto_venta(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '8️⃣' and admin_Ventas:
            await poner_pieza_venta(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '9️⃣' and admin_Ventas:
            await reponer_stock_piezas(ctx)
            await menu_ventas(ctx, admin_Ventas=admin_Ventas)
        elif str(reaction.emoji) == '🔟' and admin_Ventas:
            await ctx.send("Sesión cerrada.")
            await menu(ctx)
#%% Menu taller
async def menu_taller(ctx, admin=False):

    # Comprobar si el usuario tiene el rol "autorizado"
    if "autorizado" not in [role.name for role in ctx.author.roles]:
        return

    # Mensaje inicial del menú
    if admin:
        taller_msg = (
            "Menú del Taller:\n"
            "1. Llevar moto al taller.\n"
            "2. Ver estado de una moto.\n"
            "3. Eliminar moto del taller.\n"
            "4. Ver todas las motos del taller.\n"
            "5. Cambiar estado de una moto.\n"
            "6. Cerrar sesión."
        )
    else:
        taller_msg = (
            "Menú del Taller:\n"
            "1. Llevar moto al taller.\n"
            "2. Ver estado de una moto.\n"
            "3. Recoger moto.\n"
            "4. Opciones administrador.\n"
            "5. Cerrar sesión."
        )

    taller_message = await ctx.send(taller_msg)

    await taller_message.add_reaction('1️⃣')
    await taller_message.add_reaction('2️⃣')
    await taller_message.add_reaction('3️⃣')
    await taller_message.add_reaction('4️⃣')
    await taller_message.add_reaction('5️⃣')

    # Añadir opciones si eres admin
    if admin:
        await taller_message.add_reaction('6️⃣')

    def check(reaction, user): #
        if admin:
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']
        else:
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send('¡Tiempo agotado!')
    else: # Implementar la lógica de cada opción
        if str(reaction.emoji) == '1️⃣':
            try:
                await llevar_moto_taller(ctx)
                await menu_taller(ctx, admin=admin)
            except asyncio.TimeoutError:
                await ctx.send('¡Tiempo agotado para introducir el modelo de la moto!')
        elif str(reaction.emoji) == '2️⃣':
            await ver_estado_1_moto(ctx)
            await menu_taller(ctx, admin=admin)
        elif str(reaction.emoji) == '3️⃣':
            if admin:
                try:
                    await ctx.send("Introduce el ID de la moto para eliminar:")
                    id_msg = await bot.wait_for('message', timeout=30.0,
                    check=lambda message: message.author == ctx.author)
                    id_moto = id_msg.content

                    await eliminar_moto_taller(ctx, id_moto)
                    await menu_taller(ctx, admin=True)
                except asyncio.TimeoutError:
                    await ctx.send('¡Tiempo agotado para introducir el ID de la moto!')
            else:
                await recoger_moto_taller(ctx)
                await menu_taller(ctx, admin)
        elif str(reaction.emoji) == '4️⃣':
            if admin:
                await listar_motos_taller(ctx)
                await menu_taller(ctx, admin=admin)

            else:
                await ctx.send("Introduce la contraseña de administrador:")
                try:
                    msg = await bot.wait_for('message', timeout=30.0,
                                             check=lambda message: message.author == ctx.author)
                    if msg.content == contraseña_admin_taller:
                        await ctx.send("**Contraseña correcta**. Aquí tienes las opciones adicionales...")
                        await menu_taller(ctx, admin=True)
                    else:
                        await ctx.send("Contraseña incorrecta.")
                        await menu_taller(ctx, admin)
                except asyncio.TimeoutError:
                    await ctx.send('¡Tiempo agotado para introducir la contraseña de administrador!')
        elif str(reaction.emoji) == '5️⃣':
            if admin:
                await cambiar_estado(ctx)
                await menu_taller(ctx, admin=admin)
            else:
                await ctx.send("Saliendo del menú.")
                await menu(ctx)
        elif str(reaction.emoji) == '6️⃣' and admin:
            await ctx.send("Saliendo del menú.")
            await menu(ctx)


#%% Ejecutar el bot

bot.run('Token aqui, copiale')
