package com.hospital;

public class Main {
    public static void main(String[] args) {
        SistemaEmergencia sistema = new SistemaEmergencia();
        sistema.cargarPacientes("pacientes.txt");
        sistema.mostrarMenuPrincipal();
    }
}