package com.hospital;

import java.io.*;
import java.util.*;

public class Paciente implements Comparable<Paciente> {
    private String nombre;
    private String sintoma;
    private char prioridad;

    // Constructor
    public Paciente(String nombre, String sintoma, char prioridad) {
        this.nombre = nombre;
        this.sintoma = sintoma;
        this.prioridad = prioridad;
    }

    // Getters
    public String getNombre() {
        return nombre;
    }

    public String getSintoma() {
        return sintoma;
    }

    public char getPrioridad() {
        return prioridad;
    }

    // Implementación de compareTo para ordenar por prioridad (A tiene más prioridad que B, C, etc.)
    @Override
    public int compareTo(Paciente otro) {
        return Character.compare(this.prioridad, otro.prioridad);
    }

    // Método toString para imprimir correctamente el objeto
    @Override
    public String toString() {
        return nombre + ", " + sintoma + ", " + prioridad;
    }

    // Método para leer pacientes desde un archivo de texto
    public static List<Paciente> leerPacientes(String archivo) {
        List<Paciente> listaPacientes = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(archivo))) {
            String linea;
            while ((linea = br.readLine()) != null) {
                String[] datos = linea.split(", ");
                if (datos.length == 3) {
                    listaPacientes.add(new Paciente(datos[0], datos[1], datos[2].charAt(0)));
                }
            }
        } catch (IOException e) {
            System.out.println("Error al leer el archivo: " + e.getMessage());
        }
        return listaPacientes;
    }
}

