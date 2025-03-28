package com.hospital;


import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class VectorHeapTest {

    private VectorHeap<Paciente> heap;

    @BeforeEach
    void setUp() {
        heap = new VectorHeap<>();
    }

    @Test
    void testAddAndRemove() {
        Paciente paciente1 = new Paciente("Juan", "Fiebre", 'B');
        Paciente paciente2 = new Paciente("Ana", "Dolor de cabeza", 'A');
        Paciente paciente3 = new Paciente("Luis", "Tos", 'C');
        
        // Agregar pacientes al heap
        heap.add(paciente1);
        heap.add(paciente2);
        heap.add(paciente3);

        // Comprobar que el primer paciente (con mayor prioridad) es el esperado
        assertEquals(paciente2, heap.getFirst(), "El paciente con mayor prioridad debe ser Ana");

        // Eliminar el paciente de mayor prioridad y comprobar el siguiente
        heap.remove();
        assertEquals(paciente1, heap.getFirst(), "Después de eliminar a Ana, el siguiente debe ser Juan");

        // Eliminar el siguiente paciente y comprobar el último
        heap.remove();
        assertEquals(paciente3, heap.getFirst(), "Después de eliminar a Juan, el siguiente debe ser Luis");
        
        // Eliminar el último paciente y comprobar que el heap esté vacío
        heap.remove();
        assertTrue(heap.isEmpty(), "El heap debe estar vacío después de eliminar todos los pacientes");
    }

    @Test
    void testIsEmpty() {
        assertTrue(heap.isEmpty(), "El heap debería estar vacío al inicio");

        Paciente paciente = new Paciente("Pedro", "Dolor de estómago", 'B');
        heap.add(paciente);

        assertFalse(heap.isEmpty(), "El heap no debería estar vacío después de agregar un paciente");
    }

    @Test
    void testSize() {
        assertEquals(0, heap.size(), "El tamaño del heap debería ser 0 al inicio");

        Paciente paciente = new Paciente("Maria", "Cansancio", 'C');
        heap.add(paciente);

        assertEquals(1, heap.size(), "El tamaño del heap debería ser 1 después de agregar un paciente");

        heap.remove();
        assertEquals(0, heap.size(), "El tamaño del heap debería ser 0 después de eliminar el paciente");
    }
}
