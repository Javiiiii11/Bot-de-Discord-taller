from flask import Flask, jsonify, request
from waitress import serve

app = Flask(__name__)

# Simulación de base de datos en memoria
motos_taller = [
    {'id': 1, 'marca': 'Yamaha', 'modelo': 'R1', 'año': 2020, 'estado': 'Reparada'},
    {'id': 2, 'marca': 'Honda', 'modelo': 'CBR 600', 'año': 2019, 'estado': 'Reparada'},
    {'id': 3, 'marca': 'Suzuki', 'modelo': 'GSX-R 1000', 'año': 2021, 'estado': 'En reparación'},
    {'id': 4, 'marca': 'Ducati', 'modelo': 'Panigale V4', 'año': 2022, 'estado': 'En reparación'},
    {'id': 5, 'marca': 'Kawasaki', 'modelo': 'Ninja ZX-10R', 'año': 2020, 'estado': 'En reparación'}
]
# Simulación de base de datos de piezas en memoria
piezas = [
    {'referencia': 'REF001', 'nombre': 'Filtro de aceite', 'disponible': True, 'cantidad': 10},
    {'referencia': 'REF002', 'nombre': 'Cadena', 'disponible': True, 'cantidad': 15},
    {'referencia': 'REF003', 'nombre': 'Pastillas de freno', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF004', 'nombre': 'Neumático trasero', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF005', 'nombre': 'Espejo izquierdo', 'disponible': True, 'cantidad': 12},
    {'referencia': 'REF006', 'nombre': 'Filtro de aire', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF007', 'nombre': 'Faros LED', 'disponible': True, 'cantidad': 5},
    {'referencia': 'REF008', 'nombre': 'Disco de freno delantero', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF009', 'nombre': 'Batería', 'disponible': True, 'cantidad': 7},
    {'referencia': 'REF010', 'nombre': 'Amortiguador trasero', 'disponible': True, 'cantidad': 9},
    {'referencia': 'REF011', 'nombre': 'Escape deportivo', 'disponible': True, 'cantidad': 6},
    {'referencia': 'REF012', 'nombre': 'Carenado frontal', 'disponible': True, 'cantidad': 4},
    {'referencia': 'REF013', 'nombre': 'Rueda delantera', 'disponible': True, 'cantidad': 11},
    {'referencia': 'REF014', 'nombre': 'Horquilla delantera', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF015', 'nombre': 'Pinza de freno trasera', 'disponible': True, 'cantidad': 10},
    {'referencia': 'REF016', 'nombre': 'Pedal de freno', 'disponible': True, 'cantidad': 14},
    {'referencia': 'REF017', 'nombre': 'Manillar', 'disponible': True, 'cantidad': 13},
    {'referencia': 'REF018', 'nombre': 'Parabrisas', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF019', 'nombre': 'Kit de transmisión', 'disponible': True, 'cantidad': 7},
    {'referencia': 'REF020', 'nombre': 'Bobina de encendido', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF021', 'nombre': 'Llanta trasera', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF022', 'nombre': 'Radiador', 'disponible': True, 'cantidad': 6},
    {'referencia': 'REF023', 'nombre': 'Kit de luces intermitentes', 'disponible': True, 'cantidad': 9},
    {'referencia': 'REF024', 'nombre': 'Sensor de velocidad', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF025', 'nombre': 'Depósito de combustible', 'disponible': True, 'cantidad': 5},
    {'referencia': 'REF026', 'nombre': 'Caballete central', 'disponible': True, 'cantidad': 7},
    {'referencia': 'REF027', 'nombre': 'Tubo de escape', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF028', 'nombre': 'Asiento', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF029', 'nombre': 'Cilindro maestro de freno', 'disponible': True, 'cantidad': 10},
    {'referencia': 'REF030', 'nombre': 'Bujías', 'disponible': True, 'cantidad': 12},
    {'referencia': 'REF031', 'nombre': 'Correa de distribución', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF032', 'nombre': 'Tapa de aceite', 'disponible': True, 'cantidad': 11},
    {'referencia': 'REF033', 'nombre': 'Soporte de matrícula', 'disponible': True, 'cantidad': 9},
    {'referencia': 'REF034', 'nombre': 'Tubo de escape cromado', 'disponible': True, 'cantidad': 6},
    {'referencia': 'REF035', 'nombre': 'Filtro de combustible', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF036', 'nombre': 'Válvula de presión', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF037', 'nombre': 'Protector de manos', 'disponible': True, 'cantidad': 7},
    {'referencia': 'REF038', 'nombre': 'Cojín del asiento', 'disponible': True, 'cantidad': 5},
    {'referencia': 'REF039', 'nombre': 'Conector de batería', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF040', 'nombre': 'Tapa del radiador', 'disponible': True, 'cantidad': 6},
    {'referencia': 'REF041', 'nombre': 'Cámara de aire', 'disponible': True, 'cantidad': 10},
    {'referencia': 'REF042', 'nombre': 'Frenos de disco', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF043', 'nombre': 'Manguera de freno', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF044', 'nombre': 'Lubricante de cadena', 'disponible': True, 'cantidad': 12},
    {'referencia': 'REF045', 'nombre': 'Cuerpo de acelerador', 'disponible': True, 'cantidad': 9},
    {'referencia': 'REF046', 'nombre': 'Interruptor de encendido', 'disponible': True, 'cantidad': 7},
    {'referencia': 'REF047', 'nombre': 'Soporte del motor', 'disponible': True, 'cantidad': 8},
    {'referencia': 'REF048', 'nombre': 'Sensor de temperatura', 'disponible': True, 'cantidad': 1},
    {'referencia': 'REF049', 'nombre': 'Cárter de motor', 'disponible': True, 'cantidad': 6},
    {'referencia': 'REF050', 'nombre': 'Calefacción de puños', 'disponible': True, 'cantidad': 5}
]

# Nuevas motos
motos_nuevas = [
    {'id': 1, 'marca': 'Yamaha', 'modelo': 'MT-07', 'año': 2021, 'precio': 7000},
    {'id': 2, 'marca': 'Kawasaki', 'modelo': 'Z900', 'año': 2022, 'precio': 9500},
    {'id': 3, 'marca': 'Ducati', 'modelo': 'Monster 821', 'año': 2020, 'precio': 8500},
    {'id': 4, 'marca': 'Honda', 'modelo': 'CB650R', 'año': 2023, 'precio': 8200},
    {'id': 5, 'marca': 'Suzuki', 'modelo': 'SV650', 'año': 2022, 'precio': 7500},
    {'id': 6, 'marca': 'BMW', 'modelo': 'F 900 R', 'año': 2021, 'precio': 9500},
    {'id': 7, 'marca': 'Triumph', 'modelo': 'Street Triple', 'año': 2022, 'precio': 9900},
    {'id': 8, 'marca': 'KTM', 'modelo': '790 Duke', 'año': 2020, 'precio': 8300},
    {'id': 9, 'marca': 'Harley-Davidson', 'modelo': 'Iron 883', 'año': 2019, 'precio': 12000},
    {'id': 10, 'marca': 'Aprilia', 'modelo': 'RS 660', 'año': 2021, 'precio': 10500}
]


#%% API piezas
@app.route('/motos/piezas', methods=['GET'])
def obtener_piezas():
    return jsonify(piezas), 200

@app.route('/motos/piezas/<string:referencia>', methods=['GET'])
def obtener_pieza(referencia):
    pieza = next((p for p in piezas if p['referencia'] == referencia), None)
    if pieza:
        return jsonify(pieza), 200
    else:
        return jsonify({'mensaje': 'Pieza no encontrada'}), 404

@app.route('/motos/piezas', methods=['POST'])
def agregar_pieza():
    try:
        nueva_pieza = request.get_json()
        if not all(key in nueva_pieza for key in ('referencia','nombre', 'disponible')):
            return jsonify({'mensaje': 'Datos incompletos, se requieren nombre y disponibilidad.'}), 400
        piezas.append(nueva_pieza)
        return jsonify(nueva_pieza), 201
    except Exception as e:
        app.logger.error(f"Error al agregar pieza: {e}")
        return jsonify({'mensaje': 'Error interno del servidor'}), 500

@app.route('/motos/piezas/<string:referencia>', methods=['PUT'])
def actualizar_pieza(referencia):
    pieza = next((p for p in piezas if p['referencia'] == referencia), None)
    if pieza:
        datos_actualizados = request.get_json()
        pieza.update(datos_actualizados)
        return jsonify(pieza), 200
    else:
        return jsonify({'mensaje': 'Pieza no encontrada'}), 404

@app.route('/motos/piezas/<string:referencia>/comprar', methods=['POST'])
def comprar_pieza(referencia):
    pieza = next((p for p in piezas if p['referencia'] == referencia), None)

    if pieza:
        if pieza['disponible']:
            pieza['disponible'] = False  # Marcar la pieza como no disponible (vendida)
            return jsonify({"mensaje": f"Pieza {referencia} comprada exitosamente."}), 200
        else:
            return jsonify({"mensaje": "Pieza no disponible."}), 400
    else:
        return jsonify({"mensaje": "Pieza no encontrada."}), 404
@app.route('/motos/piezas/<string:referencia>', methods=['DELETE'])
def eliminar_pieza(referencia):
    global piezas
    piezas = [p for p in piezas if p['referencia'] != referencia]
    return jsonify({'mensaje': 'Pieza eliminada'}), 200

# %% API motos taller
@app.route('/motos/taller', methods=['GET'])
def obtener_motos_taller():
    return jsonify(motos_taller), 200

@app.route('/motos/taller/<int:moto_id>', methods=['GET'])
def obtener_moto_taller(moto_id):
    moto = next((m for m in motos_taller if m['id'] == moto_id), None)
    if moto:
        return jsonify(moto), 200
    else:
        return jsonify({'mensaje': 'Moto no encontrada'}), 404

@app.route('/motos/taller', methods=['POST'])
def agregar_moto_taller():
    nueva_moto = request.get_json()
    if not all(key in nueva_moto for key in ('modelo', 'año', 'estado')):
        return jsonify({'mensaje': 'Datos incompletos, se requieren modelo, año y estado.'}), 400
    nuevo_id = max(m['id'] for m in motos_taller) + 1 if motos_taller else 1
    nueva_moto['id'] = nuevo_id
    motos_taller.append(nueva_moto)
    return jsonify(nueva_moto), 201

@app.route('/motos/taller/<int:moto_id>', methods=['PUT'])
def actualizar_moto_taller(moto_id):
    moto = next((m for m in motos_taller if m['id'] == moto_id), None)
    if moto:
        datos_actualizados = request.get_json()
        moto.update(datos_actualizados)
        return jsonify(moto), 200
    else:
        return jsonify({'mensaje': 'Moto no encontrada'}), 404

@app.route('/motos/taller/<int:moto_id>', methods=['DELETE'])
def eliminar_moto_taller(moto_id):
    global motos_taller
    motos_taller = [m for m in motos_taller if m['id'] != moto_id]
    return jsonify({'mensaje': 'Moto eliminada del taller'}), 200

#%% API motos nuevas
@app.route('/motos/nuevas', methods=['GET'])
def obtener_motos_nuevas():
    return jsonify(motos_nuevas), 200

@app.route('/motos/nuevas/<int:moto_id>', methods=['GET'])
def obtener_moto_nueva(moto_id):
    moto = next((m for m in motos_nuevas if m['id'] == moto_id), None)
    if moto:
        return jsonify(moto), 200
    else:
        return jsonify({'mensaje': 'Moto no encontrada'}), 404

@app.route('/motos/nuevas', methods=['POST'])
def agregar_moto_nueva():
    nueva_moto = request.get_json()
    if not all(key in nueva_moto for key in ('marca', 'modelo', 'año', 'precio')):
        return jsonify({'mensaje': 'Datos incompletos, se requieren marca, modelo, año y precio'}), 400
    nuevo_id = max(m['id'] for m in motos_nuevas) + 1 if motos_nuevas else 1
    nueva_moto['id'] = nuevo_id
    motos_nuevas.append(nueva_moto)
    return jsonify(nueva_moto), 201

@app.route('/motos/nuevas/<int:moto_id>', methods=['PUT'])
def actualizar_moto_nueva(moto_id):
    moto = next((m for m in motos_nuevas if m['id'] == moto_id), None)
    if moto:
        datos_actualizados = request.get_json()
        moto.update(datos_actualizados)
        return jsonify(moto), 200
    else:
        return jsonify({'mensaje': 'Moto no encontrada'}), 404

@app.route('/motos/nuevas/<int:moto_id>', methods=['DELETE'])
def eliminar_moto_nueva(moto_id):
    global motos_nuevas
    motos_nuevas = [m for m in motos_nuevas if m['id'] != moto_id]
    return jsonify({'mensaje': 'Moto eliminada'}), 200

#%% Ejecutar la aplicación usando waitress para mantener el servidor abierto
if __name__ == '__main__':
    serve(app, host='0.0.0.0', port=5000)

@app.route('/motos/nuevas/<int:moto_id>/comprar', methods=['DELETE'])
def comprar_moto_nueva(moto_id):
    # Log the current list of motos_nuevas and the moto_id being searched

    moto = next((m for m in motos_nuevas if m['id'] == moto_id), None)
    if moto:
        motos_nuevas.remove(moto)
        return jsonify({'mensaje': 'Moto comprada exitosamente'}), 200
    else:
        return jsonify({'mensaje': 'Moto no encontrada'}), 404