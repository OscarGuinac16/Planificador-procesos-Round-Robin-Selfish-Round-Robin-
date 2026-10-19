# CPU Scheduling Algorithms Simulator

This project is an interactive web application that simulates the behavior of Operating System CPU scheduling algorithms. It allows you to visualize process execution through a dynamic Gantt chart and calculates completion, turnaround, and waiting times.

---

## 1. Arquitectura y Tecnologías
El sistema está construido bajo una arquitectura cliente-servidor separando estrictamente la lógica matemática de la interfaz visual:
* **Backend (Lógica):** Desarrollado en **Python** utilizando el framework **FastAPI**. Se encarga de procesar las colas, ejecutar los cálculos matemáticos ciclo por ciclo y devolver los resultados.
* **Frontend (Vista):** Construido con **HTML5, CSS3 y JavaScript puro**. Realiza peticiones asíncronas a la API y renderiza dinámicamente el diagrama de Gantt con colores y la tabla de resultados.

## 2. Algoritmos Implementados
* **Ronda (Round Robin - RR):** Algoritmo apropiativo que asigna a cada proceso una porción de tiempo equitativa y fija llamada **Quantum**.
* **Ronda Egoísta (Selfish Round Robin - SRR):** Variante avanzada que divide a los procesos en dos colas: "Nuevos" y "Aceptados". Utiliza una **Tasa a** y una **Tasa b** para incrementar la prioridad de los procesos a medida que esperan, decidiendo en qué momento los procesos nuevos son aceptados para competir por la CPU.

## 3. Instalación y Ejecución

1. Clona este repositorio en tu máquina local.
2. Abre la terminal en la carpeta del proyecto y asegúrate de instalar las dependencias necesarias:
   ```bash
   pip install fastapi uvicorn pydantic