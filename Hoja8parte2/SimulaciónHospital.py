import SimulaciónHospital
import random
import statistics
import simpy

NUM_ENFERMERAS = 6
NUM_DOCTORES = 6
NUM_MAQUINAS = 4
Tiempo_Prom_Ev = 10
Tiempo_Prom_Doc = 11
Tiempo_Prom_Enf = 50
TIEMPO_SIMULACION = 480
# Variables para estadísticas
Pacientes_Tratados = 0
tiempos_espera_triage = []
tiempos_espera_doctor = []
tiempos_espera_maquina = []
tiempos_totales = []
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
    tiempo_solicitud_triage = env.now
    with hospital.enfermeras.request(priority=1) as solicitud:
        yield solicitud
        tiempo_inicio_triage = env.now
        tiempo_espera_triage = tiempo_inicio_triage - tiempo_solicitud_triage
        tiempos_espera_triage.append(tiempo_espera_triage)

        print(
            f"Paciente {id} comienza triage con enfermera en tiempo {env.now:.1f} (esperó {tiempo_espera_triage:.1f})")

        # Tiempo de enfermear triage
        tiempo_triage = random.expovariate(1.0 / hospital.tiempo_prom_enfermera)
        yield env.timeout(tiempo_triage)

        # Asigna severidad
        severidad = random.randint(1, 5)
        severidades_pacientes[severidad] += 1
        print(f"Paciente {id} termina triage en tiempo {env.now:.1f}. Severidad asignada: {severidad}")

    # Atencion con el doctor
    tiempo_solicitud_doctor = env.now
    with hospital.doctores.request(priority=severidad) as solicitud:
        yield solicitud
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

    tiempo_solicitud_maquina = env.now
    with hospital.maquinas.request(priority=severidad) as solicitud:
        yield solicitud
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


def imprimir_estadisticas():
    """Imprime estadísticas de la simulación"""
    print("\n---------- ESTADÍSTICAS DE LA SIMULACIÓN ----------")
    print(f"Total de pacientes tratados: {Pacientes_Tratados}")

    if tiempos_espera_triage:
        print(f"\nTIEMPOS DE ESPERA:")
        print(f"Tiempo de espera promedio para triage: {statistics.mean(tiempos_espera_triage):.2f}")
        print(f"Tiempo de espera máximo para triage: {max(tiempos_espera_triage):.2f}")

    if tiempos_espera_doctor:
        print(f"Tiempo de espera promedio para doctor: {statistics.mean(tiempos_espera_doctor):.2f}")
        print(f"Tiempo de espera máximo para doctor: {max(tiempos_espera_doctor):.2f}")

    if tiempos_espera_maquina:
        print(f"Tiempo de espera promedio para máquina: {statistics.mean(tiempos_espera_maquina):.2f}")
        print(f"Tiempo de espera máximo para máquina: {max(tiempos_espera_maquina):.2f}")

    if tiempos_totales:
        print(f"\nTIEMPO TOTAL EN SISTEMA:")
        print(f"Tiempo promedio total en sistema: {statistics.mean(tiempos_totales):.2f}")
        print(f"Tiempo mínimo en sistema: {min(tiempos_totales):.2f}")
        print(f"Tiempo máximo en sistema: {max(tiempos_totales):.2f}")

    print("\nDISTRIBUCIÓN DE SEVERIDAD:")
    for severidad, cantidad in severidades_pacientes.items():
        if cantidad > 0:
            print(f"Severidad {severidad}: {cantidad} pacientes ({cantidad / Pacientes_Tratados * 100:.1f}%)")



def main():
    env = simpy.Environment()
    hospital = Hospital(env, NUM_ENFERMERAS, NUM_DOCTORES, NUM_MAQUINAS)

    hospital.run()

    env.run(until=TIEMPO_SIMULACION)

    imprimir_estadisticas()


if __name__ == "__main__":
    main()
