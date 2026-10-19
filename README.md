# CPU Scheduling Algorithms Simulator

This project is an interactive web application that simulates the behavior of Operating System CPU scheduling algorithms. It allows you to visualize process execution through a dynamic Gantt chart and calculates completion, turnaround, and waiting times.

---

## 1. Architecture and Technologies
The system is built on a client-server architecture, strictly separating mathematical logic from the visual interface:
* **Backend (Logic):** Developed in **Python** using the **FastAPI** framework. It handles process queues, executes cycle-by-cycle mathematical calculations, and returns the results.
* **Frontend (View):** Built with **HTML5, CSS3, and vanilla JavaScript**. It makes asynchronous requests to the API and dynamically renders the color-coded Gantt chart and results table.

## 2. Implemented Algorithms
* **Round Robin (RR):** A preemptive algorithm that assigns each process an equal and fixed time slice called a **Quantum**.
* **Selfish Round Robin (SRR):** An advanced variant that divides processes into two queues: "New" and "Accepted". It uses a **Rate a** and **Rate b** to increase the priority of waiting processes, determining exactly when new processes are accepted to compete for the CPU.

## 3. Installation and Execution
1. Clone this repository to your local machine.
2. Open the terminal in the project folder and install the required dependencies:
   ```bash
   pip install fastapi uvicorn pydantic