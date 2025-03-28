package com.hospital;

import java.util.List;

public class Main {
    public static void main(String[] args) {
        List<Paciente> pacientes = Paciente.leerPacientes("ht8/src/main/resources/pacientes.txt");
        VectorHeap<Paciente> colaPacientes = new VectorHeap<>(); 

        for (Paciente p : pacientes) {
            colaPacientes.add(p);
        }

        // 2. Obtener pacientes ordenados
         List<Paciente> pacientesOrdenados = colaPacientes.getOrdenados();

                // 3. Imprimir en consola
                System.out.println("Lista de Pacientes Ordenados por Prioridad:");
                for (Paciente p : pacientesOrdenados) {
                    System.out.println(p);
                }

        colaPacientes.guardarEnCSV("ht8/src/main/resources/pacientes_ordenados.csv");
    }

    
}

