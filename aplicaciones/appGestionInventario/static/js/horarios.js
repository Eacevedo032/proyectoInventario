// horarios.js - Funciones unificadas para manejo de horarios

/**
 * Convierte una hora en formato 24h a formato 12h AM/PM
 * @param {string} hora24 - Hora en formato 24h (HH:MM)
 * @returns {string} Hora en formato 12h (H:MM AM/PM)
 */
function convertir24a12(hora24) {
    if (!hora24 || !hora24.includes(':')) return hora24;
    
    const [horaStr, minuto] = hora24.split(':');
    const hora = parseInt(horaStr);
    let hora12, periodo;
    
    if (hora === 0) {
        hora12 = 12;
        periodo = 'AM';
    } else if (hora < 12) {
        hora12 = hora;
        periodo = 'AM';
    } else if (hora === 12) {
        hora12 = 12;
        periodo = 'PM';
    } else {
        hora12 = hora - 12;
        periodo = 'PM';
    }
    
    const minutosFormateados = minuto.length === 1 ? '0' + minuto : minuto;
    return `${hora12}:${minutosFormateados} ${periodo}`;
}

/**
 * Convierte una hora en formato 12h AM/PM a formato 24h
 * @param {number} hora - Hora (1-12)
 * @param {number|string} minuto - Minutos (0-59)
 * @param {string} periodo - 'AM' o 'PM'
 * @returns {string} Hora en formato 24h (HH:MM)
 */
function convertir12a24(hora, minuto, periodo) {
    hora = parseInt(hora);
    minuto = parseInt(minuto);
    
    // Asegurar que los minutos tengan dos dígitos
    const minutosFormateados = minuto < 10 ? '0' + minuto : minuto;
    
    if (periodo === 'AM') {
        if (hora === 12) {
            return `00:${minutosFormateados}`;
        } else {
            return `${hora < 10 ? '0' + hora : hora}:${minutosFormateados}`;
        }
    } else { // PM
        if (hora === 12) {
            return `12:${minutosFormateados}`;
        } else {
            return `${hora + 12}:${minutosFormateados}`;
        }
    }
}

/**
 * Convierte todas las horas en elementos con clase .hora-12h de 24h a 12h
 */
function convertirHorasMostradas() {
    const celdasHora = document.querySelectorAll('.hora-12h');
    
    celdasHora.forEach(celda => {
        if (celda.textContent.includes(':')) {
            celda.textContent = convertir24a12(celda.textContent.trim());
        }
    });
}

/**
 * Configura los formularios para convertir horas a formato 24h antes de enviar
 * @param {string} formId - ID del formulario
 * @param {object} config - Configuración de los campos
 */
function configurarFormularioHorario(formId, config) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        // Convertir hora de inicio
        const horaInicio = parseInt(document.getElementById(config.horaInicioId).value);
        const minutoInicio = document.getElementById(config.minutoInicioId).value;
        const periodoInicio = document.getElementById(config.periodoInicioId).value;
        document.getElementById(config.horaInicioMilitarId).value = 
            convertir12a24(horaInicio, minutoInicio, periodoInicio);
        
        // Convertir hora de fin
        const horaFin = parseInt(document.getElementById(config.horaFinId).value);
        const minutoFin = document.getElementById(config.minutoFinId).value;
        const periodoFin = document.getElementById(config.periodoFinId).value;
        document.getElementById(config.horaFinMilitarId).value = 
            convertir12a24(horaFin, minutoFin, periodoFin);
        
        // Validación del formulario
        if (!form.checkValidity()) {
            e.preventDefault();
            e.stopPropagation();
        }
        form.classList.add('was-validated');
    });
}

/**
 * Configuración inicial cuando el DOM está cargado
 */
document.addEventListener('DOMContentLoaded', function() {
    // Convertir horas mostradas en tablas
    convertirHorasMostradas();
    
    // Configurar formularios específicos
    configurarFormularioHorario('horarioForm', {
        horaInicioId: 'hora_inicio',
        minutoInicioId: 'minuto_inicio',
        periodoInicioId: 'periodo_inicio',
        horaInicioMilitarId: 'hora_inicio_militar',
        horaFinId: 'hora_fin',
        minutoFinId: 'minuto_fin',
        periodoFinId: 'periodo_fin',
        horaFinMilitarId: 'hora_fin_militar'
    });
    
    configurarFormularioHorario('editarHorarioForm', {
        horaInicioId: 'hora_inicio',
        minutoInicioId: 'minuto_inicio',
        periodoInicioId: 'periodo_inicio',
        horaInicioMilitarId: 'hora_inicio_militar',
        horaFinId: 'hora_fin',
        minutoFinId: 'minuto_fin',
        periodoFinId: 'periodo_fin',
        horaFinMilitarId: 'hora_fin_militar'
    });
    
    configurarFormularioHorario('reservaForm', {
        horaInicioId: 'hora_inicio',
        minutoInicioId: 'minuto_inicio',
        periodoInicioId: 'hora_inicio_periodo',
        horaInicioMilitarId: 'hora_inicio_militar',
        horaFinId: 'hora_fin',
        minutoFinId: 'minuto_fin',
        periodoFinId: 'hora_fin_periodo',
        horaFinMilitarId: 'hora_fin_militar'
    });
    
    // Configurar validación para todos los formularios con clase .needs-validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms)
        .forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
});