// Mostrar u ocultar las tasas a y b dependiendo del algoritmo seleccionado
function mostrarOcultarControles() {
    const alg = document.getElementById('algoritmo').value;
    document.getElementById('controles_egoista').style.display = (alg === 'ronda_egoista') ? 'inline' : 'none';
}

// Diccionario de colores para el diagrama de Gantt
const coloresProcesos = {
    'A': { bg: '#90EE90', text: '#000' }, // Verde claro
    'B': { bg: '#8B0000', text: '#FFF' }, // Rojo oscuro
    'C': { bg: '#FFFF00', text: '#000' }, // Amarillo
    'D': { bg: '#FFA500', text: '#000' }, // Naranja
    'E': { bg: '#800080', text: '#FFF' }, // Morado
    'F': { bg: '#00BFFF', text: '#000' }, // Celeste
    'G': { bg: '#ADD8E6', text: '#000' }, // Azul muy claro
    'Vacio': { bg: '#FFFFFF', text: '#000'}
};

async function calcular() {
    const algoritmo = document.getElementById('algoritmo').value;
    const quantum = parseInt(document.getElementById('quantum').value);
    
    // Tomar las tasas si existen en el HTML, de lo contrario usar valores por defecto
    const inputTasaA = document.getElementById('tasa_a');
    const inputTasaB = document.getElementById('tasa_b');
    const tasa_a = parseInt(inputTasaA ? inputTasaA.value : 2);
    const tasa_b = parseInt(inputTasaB ? inputTasaB.value : 1);
    
    // Recolectar datos de la tabla de ingreso
    const filas = document.querySelectorAll('#body-ingreso tr');
    const procesos = [];
    
    filas.forEach(fila => {
        const celdas = fila.querySelectorAll('td');
        const nombre = celdas[0].innerText;
        const llegada = parseInt(celdas[1].querySelector('input').value);
        const cpu = parseInt(celdas[2].querySelector('input').value);
        
        procesos.push({ nombre, llegada, cpu });
    });

    // Construir la petición JSON
    const payload = {
        algoritmo: algoritmo,
        quantum: quantum,
        tasa_a: tasa_a,
        tasa_b: tasa_b,
        procesos: procesos
    };

    // Enviar a Python (FastAPI)
    try {
        const response = await fetch('/api/calcular', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        
        if(data.error) {
            alert(data.error);
            return;
        }

        mostrarResultados(data);
    } catch (error) {
        alert("Error de conexión con el servidor.");
        console.error(error);
    }
}

function mostrarResultados(data) {
    document.getElementById('resultados').style.display = 'block';
    
    // 1. Dibujar el Diagrama de Gantt
    const ganttContainer = document.getElementById('gantt-container');
    ganttContainer.innerHTML = '';
    
    data.gantt.forEach(proceso => {
        const div = document.createElement('div');
        div.className = 'gantt-bloque';
        div.innerText = proceso;
        
        if (coloresProcesos[proceso]) {
            div.style.backgroundColor = coloresProcesos[proceso].bg;
            div.style.color = coloresProcesos[proceso].text;
        } else {
            div.style.backgroundColor = '#ccc';
        }
        
        ganttContainer.appendChild(div);
    });

    // 2. Llenar la Tabla de Resultados
    const tbodyResultados = document.getElementById('body-resultados');
    tbodyResultados.innerHTML = '';
    
    const nombresOrdenados = Object.keys(data.tabla).sort();
    
    nombresOrdenados.forEach(nombre => {
        const info = data.tabla[nombre];
        const tr = document.createElement('tr');
        
        let colorFondo = coloresProcesos[nombre] ? coloresProcesos[nombre].bg : '#fff';
        let colorTexto = coloresProcesos[nombre] ? coloresProcesos[nombre].text : '#000';

        tr.innerHTML = `
            <td style="background-color: ${colorFondo}; color: ${colorTexto}; font-weight: bold;">${nombre}</td>
            <td>${info.llegada}</td>
            <td>${info.cpu}</td>
            <td style="font-weight: bold;">${info.t_final}</td>
            <td>${info.t_retorno}</td>
            <td>${info.t_espera}</td>
        `;
        tbodyResultados.appendChild(tr);
    });

    // 3. Mostrar Promedios
    document.getElementById('prom-retorno').innerText = data.promedios.retorno;
    document.getElementById('prom-espera').innerText = data.promedios.espera;
}