import SimulaciónHospital
import random
import statistics


NUM_ENFERMERAS = 1
NUM_DOCTORES= 2
Tiempo_Prom_Ev = 3
Tiempo_Prom_Doc = 4
Tiempo_Prom_Enf = 5
Pacientes_Tratados = 0

class Hospital:
    def __init__(self,env,NUM_ENFERMERAS,NUM_DOCTORES):
        self.env = env
        self.NUM_ENFERMERAS = simpy.Resource(env, NUM_ENFERMERAS)

    def enfermeras(self):
        
        self.Tiempo_Prom_Ev = Tiempo_Prom_Ev


