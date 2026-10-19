from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Planificador de Procesos")

# Montamos la carpeta estática
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- MODELOS DE DATOS ---
class Proceso(BaseModel):
    nombre: str
    llegada: int
    cpu: int

class PeticionAlgoritmo(BaseModel):
    algoritmo: str
    quantum: int
    tasa_a: int = 2  # Tasa de incremento de prioridad en cola nueva (para Ronda Egoísta)
    tasa_b: int = 1  # Tasa de incremento de prioridad en cola aceptada (para Ronda Egoísta)
    procesos: List[Proceso]


# --- LÓGICA ALGORITMO 1: RONDA (ROUND ROBIN) ---
def calcular_ronda(procesos_input: List[Proceso], quantum: int):
    procesos = [{"nombre": p.nombre, "llegada": p.llegada, "cpu": p.cpu, "restante": p.cpu} for p in procesos_input]
    
    tiempo_actual = 0
    cola_listos = []
    ejecucion_gantt = [] 
    resultados = {}      
    
    procesos.sort(key=lambda x: x['llegada'])
    procesos_pendientes = procesos.copy()

    def actualizar_cola(tiempo):
        llegados_ahora = [p for p in procesos_pendientes if p['llegada'] <= tiempo and p not in cola_listos]
        for p in llegados_ahora:
            cola_listos.append(p)
            procesos_pendientes.remove(p)

    while procesos_pendientes or cola_listos:
        actualizar_cola(tiempo_actual)
        
        if not cola_listos:
            tiempo_actual += 1
            ejecucion_gantt.append("Vacio")
            continue
            
        proceso_actual = cola_listos.pop(0)
        tiempo_a_ejecutar = min(proceso_actual['restante'], quantum)
        
        for _ in range(tiempo_a_ejecutar):
            ejecucion_gantt.append(proceso_actual['nombre'])
            tiempo_actual += 1
            
        proceso_actual['restante'] -= tiempo_a_ejecutar
        actualizar_cola(tiempo_actual)
        
        if proceso_actual['restante'] > 0:
            cola_listos.append(proceso_actual)
        else:
            t_final = tiempo_actual
            t_retorno = t_final - proceso_actual['llegada']
            t_espera = t_retorno - proceso_actual['cpu']
            
            resultados[proceso_actual['nombre']] = {
                "llegada": proceso_actual['llegada'], "cpu": proceso_actual['cpu'],
                "t_final": t_final, "t_retorno": t_retorno, "t_espera": t_espera
            }

    promedio_retorno = sum(p['t_retorno'] for p in resultados.values()) / len(resultados) if resultados else 0
    promedio_espera = sum(p['t_espera'] for p in resultados.values()) / len(resultados) if resultados else 0

    return {
        "gantt": ejecucion_gantt,
        "tabla": resultados,
        "promedios": {
            "retorno": round(promedio_retorno, 4),
            "espera": round(promedio_espera, 4)
        }
    }


# --- LÓGICA ALGORITMO 2: RONDA EGOÍSTA (SELFISH ROUND ROBIN) ---
def calcular_ronda_egoista(procesos_input: List[Proceso], quantum: int, a: int, b: int):
    procesos = [{"nombre": p.nombre, "llegada": p.llegada, "cpu": p.cpu, "restante": p.cpu, "prioridad": 0, "estado": "nuevo"} for p in procesos_input]
    
    tiempo_actual = 0
    ejecucion_gantt = []
    resultados = {}
    
    procesos.sort(key=lambda x: x['llegada'])
    pendientes = procesos.copy()
    cola_nuevos = []
    cola_aceptados = []
    
    proceso_actual_rr = None
    quantum_restante = 0

    while pendientes or cola_nuevos or cola_aceptados or proceso_actual_rr:
        # 1. Ingresar procesos
        llegaron_ahora = [p for p in pendientes if p['llegada'] == tiempo_actual]
        for p in llegaron_ahora:
            cola_nuevos.append(p)
            pendientes.remove(p)

        # 2. Promocionar si aceptados está vacío
        if not cola_aceptados and not proceso_actual_rr and cola_nuevos:
            max_prio = max(p['prioridad'] for p in cola_nuevos)
            promovidos = [p for p in cola_nuevos if p['prioridad'] == max_prio]
            for p in promovidos:
                p['estado'] = 'aceptado'
                cola_aceptados.append(p)
                cola_nuevos.remove(p)

        # 3. Promocionar si alcanzan prioridad
        if cola_aceptados or proceso_actual_rr:
            ref_prio = proceso_actual_rr['prioridad'] if proceso_actual_rr else cola_aceptados[0]['prioridad']
            promover = [p for p in cola_nuevos if p['prioridad'] >= ref_prio]
            for p in promover:
                p['estado'] = 'aceptado'
                p['prioridad'] = ref_prio 
                cola_aceptados.append(p)
                cola_nuevos.remove(p)

        # 4. Asignar CPU (Round Robin en aceptados)
        if not proceso_actual_rr and cola_aceptados:
            proceso_actual_rr = cola_aceptados.pop(0)
            quantum_restante = quantum

        # 5. Ejecutar ciclo
        if proceso_actual_rr:
            ejecucion_gantt.append(proceso_actual_rr['nombre'])
            proceso_actual_rr['restante'] -= 1
            quantum_restante -= 1
            
            for p in cola_nuevos: p['prioridad'] += a
            for p in cola_aceptados: p['prioridad'] += b
            proceso_actual_rr['prioridad'] += b 
            
            tiempo_actual += 1

            if proceso_actual_rr['restante'] == 0:
                t_final = tiempo_actual
                t_retorno = t_final - proceso_actual_rr['llegada']
                t_espera = t_retorno - proceso_actual_rr['cpu']
                resultados[proceso_actual_rr['nombre']] = {
                    "llegada": proceso_actual_rr['llegada'], "cpu": proceso_actual_rr['cpu'],
                    "t_final": t_final, "t_retorno": t_retorno, "t_espera": t_espera
                }
                proceso_actual_rr = None
            elif quantum_restante == 0:
                cola_aceptados.append(proceso_actual_rr)
                proceso_actual_rr = None

        else:
            ejecucion_gantt.append("Vacio")
            for p in cola_nuevos: p['prioridad'] += a
            tiempo_actual += 1

    promedio_retorno = sum(p['t_retorno'] for p in resultados.values()) / len(resultados) if resultados else 0
    promedio_espera = sum(p['t_espera'] for p in resultados.values()) / len(resultados) if resultados else 0

    return {
        "gantt": ejecucion_gantt,
        "tabla": resultados,
        "promedios": {
            "retorno": round(promedio_retorno, 4),
            "espera": round(promedio_espera, 4)
        }
    }


# --- RUTAS DE LA API ---
@app.get("/")
async def cargar_interfaz():
    return FileResponse('static/index.html')

@app.post("/api/calcular")
async def ejecutar_algoritmos(datos: PeticionAlgoritmo):
    if datos.algoritmo == "ronda":
        return calcular_ronda(datos.procesos, datos.quantum)
    elif datos.algoritmo == "ronda_egoista":
        return calcular_ronda_egoista(datos.procesos, datos.quantum, datos.tasa_a, datos.tasa_b)
    else:
        return {"error": "Algoritmo no implementado"}