import random
import statistics
import simpy
import matplotlib.pyplot as plt

# Configuración inicial
TIEMPO_SIMULACION = 240  # 8 horas = 480 minutos
Tiempo_Prom_Ev = 20
Tiempo_Prom_Doc = 15
Tiempo_Prom_Enf = 7
NUM_ENFERMERAS = 5
NUM_DOCTORES = 4
NUM_MAQUINAS = 4

# Costos de recursos
COSTO_ENFERMERA_POR_HORA = 23.33  # Q por hora
COSTO_DOCTOR_POR_HORA = 62.5  # Q por hora
COSTO_MAQUINA_POR_DIA = 2100  # Q por día

# Variables para estadísticas
Pacientes_Tratados = 0
tiempos_espera_triage = []
tiempos_espera_doctor = []
tiempos_espera_maquina = []

# Nuevas variables para tiempos totales por etapa
tiempos_total_triage = []  # Tiempo de espera + tiempo con enfermera
tiempos_total_doctor = []  # Tiempo de espera + tiempo con doctor
tiempos_total_maquina = []  # Tiempo de espera + tiempo en máquina
tiempos_totales = []  # Tiempo total en el sistema
severidades_pacientes = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}


class Hospital:
    def __init__(self, env, num_enfermeras, num_doctores, num_maquinas):
        self.env = env
        self.enfermeras = simpy.PriorityResource(env, capacity=num_enfermeras)
        self.doctores = simpy.PriorityResource(env, capacity=num_doctores)
        self.maquinas = simpy.PriorityResource(env, capacity=num_maquinas)
        self.tiempo_prom_maquina = Tiempo_Prom_Ev
        self.tiempo_prom_doctor = Tiempo_Prom_Doc
        self.tiempo_prom_enfermera = Tiempo_Prom_Enf

    def run(self):
        self.env.process(generador_pacientes(self.env, self, 5))  # 5 minutos entre llegadas en promedio


def paciente(env, id, hospital):
    tiempo_llegada = env.now
    print(f"Paciente {id} llega al hospital en {env.now:.1f}")

    # Triage con la enfermera - asignación de severidad
    tiempo_inicio_etapa_triage = env.now

    with hospital.enfermeras.request(priority=1) as solicitud:
        tiempo_solicitud_triage = env.now
        yield solicitud

        # Registrar tiempo de espera para triage
        tiempo_inicio_triage = env.now
        tiempo_espera_triage = tiempo_inicio_triage - tiempo_solicitud_triage
        tiempos_espera_triage.append(tiempo_espera_triage)

        print(
            f"Paciente {id} comienza triage con enfermera en tiempo {env.now:.1f} (esperó {tiempo_espera_triage:.1f})")

        # Tiempo de enfermera triage
        tiempo_triage = random.expovariate(1.0 / hospital.tiempo_prom_enfermera)
        yield env.timeout(tiempo_triage)

        # Asigna severidad
        severidad = random.randint(1, 5)
        severidades_pacientes[severidad] += 1
        print(f"Paciente {id} termina triage en tiempo {env.now:.1f}. Severidad asignada: {severidad}")

    # Registrar tiempo total en etapa de triage (espera + atención)
    tiempo_total_triage = env.now - tiempo_inicio_etapa_triage
    tiempos_total_triage.append(tiempo_total_triage)
    print(f"DEBUG - Paciente {id}: Tiempo TOTAL en etapa triage: {tiempo_total_triage:.2f}")

    # Atención con el doctor
    tiempo_inicio_etapa_doctor = env.now

    with hospital.doctores.request(priority=6 - severidad) as solicitud:
        tiempo_solicitud_doctor = env.now
        yield solicitud

        # Registrar tiempo de espera para doctor
        tiempo_inicio_doctor = env.now
        tiempo_espera_doctor = tiempo_inicio_doctor - tiempo_solicitud_doctor
        tiempos_espera_doctor.append(tiempo_espera_doctor)

        print(f"Paciente {id} comienza atención con doctor en tiempo {env.now:.1f} (esperó {tiempo_espera_doctor:.1f})")

        # Tiempo con doctor
        tiempo_base_doctor = hospital.tiempo_prom_doctor
        factor_tiempo = 1.5 if severidad <= 2 else 1.0
        tiempo_doctor = random.expovariate(1.0 / (tiempo_base_doctor * factor_tiempo))
        yield env.timeout(tiempo_doctor)

        print(f"Paciente {id} termina atención con doctor en tiempo {env.now:.1f}")

    # Registra el tiempo total en etapa de doctor
    tiempo_total_doctor = env.now - tiempo_inicio_etapa_doctor
    tiempos_total_doctor.append(tiempo_total_doctor)
    print(f"DEBUG - Paciente {id}: Tiempo TOTAL en etapa doctor: {tiempo_total_doctor:.2f}")

    # Estudio en máquina
    tiempo_inicio_etapa_maquina = env.now

    with hospital.maquinas.request(priority=6 - severidad) as solicitud:
        tiempo_solicitud_maquina = env.now
        yield solicitud

        # Registra el tiempo de espera para máquina
        tiempo_inicio_maquina = env.now
        tiempo_espera_maquina = tiempo_inicio_maquina - tiempo_solicitud_maquina
        tiempos_espera_maquina.append(tiempo_espera_maquina)

        print(f"Paciente {id} comienza estudio en máquina en tiempo {env.now:.1f} (esperó {tiempo_espera_maquina:.1f})")

        # Tiempo en máquina
        tiempo_base_maquina = hospital.tiempo_prom_maquina
        factor_tiempo = 1.3 if severidad <= 3 else 0.8
        tiempo_maquina = random.expovariate(1.0 / (tiempo_base_maquina * factor_tiempo))
        yield env.timeout(tiempo_maquina)

        print(f"Paciente {id} termina estudio en máquina en tiempo {env.now:.1f}")

    # Registra el tiempo total en etapa de máquina (espera + atención)
    tiempo_total_maquina = env.now - tiempo_inicio_etapa_maquina
    tiempos_total_maquina.append(tiempo_total_maquina)
    print(f"DEBUG - Paciente {id}: Tiempo TOTAL en etapa máquina: {tiempo_total_maquina:.2f}")

    # Incrementar contador y calcular tiempo total
    global Pacientes_Tratados
    Pacientes_Tratados += 1

    tiempo_total = env.now - tiempo_llegada
    tiempos_totales.append(tiempo_total)

    print(
        f"Paciente {id} completó todo el tratamiento en tiempo {env.now:.1f}. Tiempo total: {tiempo_total:.1f}. Severidad: {severidad}")
    print(f"Total pacientes tratados: {Pacientes_Tratados}")


def generador_pacientes(env, hospital, tiempo_entre_llegadas):
    id_paciente = 0
    while True:
        # Tiempo aleatorio entre llegadas
        tiempo_llegada = random.expovariate(1.0 / tiempo_entre_llegadas)
        yield env.timeout(tiempo_llegada)

        id_paciente += 1
        env.process(paciente(env, id_paciente, hospital))


def calcular_costos(num_enfermeras, num_doctores, num_maquinas, horas_por_dia=8):
    costo_enfermeras = num_enfermeras * COSTO_ENFERMERA_POR_HORA * horas_por_dia
    costo_doctores = num_doctores * COSTO_DOCTOR_POR_HORA * horas_por_dia
    costo_maquinas = num_maquinas * COSTO_MAQUINA_POR_DIA

    costo_total = costo_enfermeras + costo_doctores + costo_maquinas

    return {
        'enfermeras': costo_enfermeras,
        'doctores': costo_doctores,
        'maquinas': costo_maquinas,
        'total': costo_total
    }

#Prompt: Podrias incluir un analisis estadístico para este programa
def imprimir_estadisticas():
    print("\n---------- ESTADÍSTICAS DE LA SIMULACIÓN ----------")
    print(f"Configuración: {NUM_ENFERMERAS} enfermeras, {NUM_DOCTORES} doctores, {NUM_MAQUINAS} máquinas")
    print(f"Total de pacientes tratados: {Pacientes_Tratados}")

    print(f"\nTIEMPOS DE ESPERA:")
    if tiempos_espera_triage:
        print(f"Tiempo de espera promedio para triage: {statistics.mean(tiempos_espera_triage):.2f}")
        print(f"Tiempo de espera máximo para triage: {max(tiempos_espera_triage):.2f}")

    if tiempos_espera_doctor:
        print(f"Tiempo de espera promedio para doctor: {statistics.mean(tiempos_espera_doctor):.2f}")
        print(f"Tiempo de espera máximo para doctor: {max(tiempos_espera_doctor):.2f}")

    if tiempos_espera_maquina:
        print(f"Tiempo de espera promedio para máquina: {statistics.mean(tiempos_espera_maquina):.2f}")
        print(f"Tiempo de espera máximo para máquina: {max(tiempos_espera_maquina):.2f}")

    print(f"\nTIEMPOS TOTALES POR ETAPA (espera + atención):")
    if tiempos_total_triage:
        print(f"Tiempo total promedio en triage: {statistics.mean(tiempos_total_triage):.2f}")
    if tiempos_total_doctor:
        print(f"Tiempo total promedio con doctor: {statistics.mean(tiempos_total_doctor):.2f}")
    if tiempos_total_maquina:
        print(f"Tiempo total promedio en máquina: {statistics.mean(tiempos_total_maquina):.2f}")

    if tiempos_totales:
        print(f"\nTIEMPO TOTAL EN SISTEMA:")
        print(f"Tiempo promedio total en sistema: {statistics.mean(tiempos_totales):.2f}")
        print(f"Tiempo mínimo en sistema: {min(tiempos_totales):.2f}")
        print(f"Tiempo máximo en sistema: {max(tiempos_totales):.2f}")

    print("\nDISTRIBUCIÓN DE SEVERIDAD:")
    for severidad, cantidad in severidades_pacientes.items():
        if cantidad > 0:
            print(f"Severidad {severidad}: {cantidad} pacientes ({cantidad / Pacientes_Tratados * 100:.1f}%)")

    # Calcular y mostrar costos
    costos = calcular_costos(NUM_ENFERMERAS, NUM_DOCTORES, NUM_MAQUINAS)
    print("\nCOSTOS DE OPERACIÓN (por día):")
    print(f"Costo enfermeras: ${costos['enfermeras']:.2f}")
    print(f"Costo doctores: ${costos['doctores']:.2f}")
    print(f"Costo máquinas: ${costos['maquinas']:.2f}")
    print(f"Costo total: ${costos['total']:.2f}")

    if Pacientes_Tratados > 0:
        costo_por_paciente = costos['total'] / Pacientes_Tratados
        print(f"Costo promedio por paciente: ${costo_por_paciente:.2f}")


def generar_graficas():
    # Crear una figura con 2 subplots (2 filas, 2 columnas)
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))

    # 1. Gráfica de tiempos TOTALES por etapa
    etapas = ['Triage', 'Doctor', 'Máquina', 'Total Sistema']
    tiempos_totales_por_etapa = [
        statistics.mean(tiempos_total_triage) if tiempos_total_triage else 0,
        statistics.mean(tiempos_total_doctor) if tiempos_total_doctor else 0,
        statistics.mean(tiempos_total_maquina) if tiempos_total_maquina else 0,
        statistics.mean(tiempos_totales) if tiempos_totales else 0
    ]

    # Imprimir valores para debugging
    print(f"\nDEBUG - Tiempos TOTALES promedio por etapa:")
    print(f"  Triage: {tiempos_totales_por_etapa[0]:.2f}")
    print(f"  Doctor: {tiempos_totales_por_etapa[1]:.2f}")
    print(f"  Máquina: {tiempos_totales_por_etapa[2]:.2f}")
    print(f"  Total Sistema: {tiempos_totales_por_etapa[3]:.2f}")

    axs[0, 0].bar(etapas, tiempos_totales_por_etapa)
    axs[0, 0].set_title('Tiempo TOTAL promedio por etapa (espera + atención)')
    axs[0, 0].set_ylabel('Minutos')

    # 2. Gráfica de tiempos de ESPERA por etapa
    etapas_espera = ['Triage', 'Doctor', 'Máquina']
    tiempos_espera = [
        statistics.mean(tiempos_espera_triage) if tiempos_espera_triage else 0,
        statistics.mean(tiempos_espera_doctor) if tiempos_espera_doctor else 0,
        statistics.mean(tiempos_espera_maquina) if tiempos_espera_maquina else 0
    ]

    print(f"\nDEBUG - Tiempos de ESPERA promedio:")
    print(f"  Triage: {tiempos_espera[0]:.2f}")
    print(f"  Doctor: {tiempos_espera[1]:.2f}")
    print(f"  Máquina: {tiempos_espera[2]:.2f}")

    axs[0, 1].bar(etapas_espera, tiempos_espera)
    axs[0, 1].set_title('Tiempos de ESPERA promedio por etapa')
    axs[0, 1].set_ylabel('Minutos')

    # 3. Gráfica de severidades
    severidades = list(severidades_pacientes.keys())
    cantidades = [severidades_pacientes[s] for s in severidades]

    axs[1, 0].bar(severidades, cantidades)
    axs[1, 0].set_title('Distribución de pacientes por severidad')
    axs[1, 0].set_xlabel('Nivel de severidad')
    axs[1, 0].set_ylabel('Cantidad de pacientes')

    # 4. Gráfica de rendimiento (pacientes por hora)
    horas_simulacion = TIEMPO_SIMULACION / 60
    pacientes_por_hora = Pacientes_Tratados / horas_simulacion

    axs[1, 1].bar(['Pacientes por hora'], [pacientes_por_hora])
    axs[1, 1].set_title('Rendimiento del hospital')
    axs[1, 1].set_ylabel('Pacientes tratados por hora')

    plt.tight_layout()
    plt.savefig('estadisticas_hospital.png')
    plt.close()

    print("\nGráficas generadas y guardadas como 'estadisticas_hospital.png'")


def main():
    # Establece la semilla
    random.seed(42)

    env = simpy.Environment()
    hospital = Hospital(env, NUM_ENFERMERAS, NUM_DOCTORES, NUM_MAQUINAS)
    hospital.run()
    env.run(until=TIEMPO_SIMULACION)

    # Mostrar estadísticas y generar gráficas
    imprimir_estadisticas()
    generar_graficas()


if __name__ == "__main__":
    main()