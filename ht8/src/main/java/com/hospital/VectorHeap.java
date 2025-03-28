package com.hospital;

import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;

public class VectorHeap<E extends Comparable<E>> implements PriorityQueue<E> {
    private ArrayList<E> data;

    public VectorHeap() {
        data = new ArrayList<>();
    }

    @Override
    public E getFirst() {
        if (isEmpty()) {
            throw new IllegalStateException("La cola de prioridad está vacía.");
        }
        return data.get(0);
    }

    @Override
    public E remove() {
        if (isEmpty()) {
            throw new IllegalStateException("La cola de prioridad está vacía.");
        }
        E min = data.get(0);
        data.set(0, data.get(data.size() - 1));
        data.remove(data.size() - 1);
        reorganizarHeap(0);
        return min;
    }

    @Override
    public void add(E value) {
        data.add(value);
        reorganizarArriba(data.size() - 1);
    }

    @Override
    public boolean isEmpty() {
        return data.isEmpty();
    }

    @Override
    public int size() {
        return data.size();
    }

    @Override
    public void clear() {
        data.clear();
    }

    private void reorganizarArriba(int index) {
        while (index > 0) {
            int parent = (index - 1) / 2;
            if (data.get(index).compareTo(data.get(parent)) < 0) {
                E temp = data.get(index);
                data.set(index, data.get(parent));
                data.set(parent, temp);
                index = parent;
            } else {
                break;
            }
        }
    }

    private void reorganizarHeap(int index) {
        int left = 2 * index + 1;
        int right = 2 * index + 2;
        int min = index;

        if (left < data.size() && data.get(left).compareTo(data.get(min)) < 0) {
            min = left;
        }
        if (right < data.size() && data.get(right).compareTo(data.get(min)) < 0) {
            min = right;
        }
        if (min != index) {
            E temp = data.get(index);
            data.set(index, data.get(min));
            data.set(min, temp);
            reorganizarHeap(min);
        }
    }

    // Nuevo método para guardar la cola ordenada en un archivo CSV
    public void guardarEnCSV(String nombreArchivo) {
        try (FileWriter writer = new FileWriter(nombreArchivo)) {
            writer.write("Paciente, Prioridad\n");

            while (!isEmpty()) {
                writer.write(remove().toString() + "\n");
            }
            System.out.println("Datos guardados en " + nombreArchivo);
        } catch (IOException e) {
            System.err.println("Error al guardar el archivo: " + e.getMessage());
        }
    }
}

