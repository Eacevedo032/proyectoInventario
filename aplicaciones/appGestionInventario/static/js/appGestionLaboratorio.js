document.addEventListener('DOMContentLoaded', () => {
    const categoriaElement = document.getElementById('categoria');
    const subcategoriaElement = document.getElementById('subcategoria');
    const solicitudElement = document.querySelector('[name="solicitud"]');

    if (categoriaElement && subcategoriaElement && solicitudElement) {
        categoriaElement.addEventListener('change', actualizarSubcategorias);
        subcategoriaElement.addEventListener('change', actualizarItems);
        solicitudElement.addEventListener('change', updateFechaUso);
    } else {
        console.error("No se encontraron los elementos con ID 'categoria', 'subcategoria' o el selector 'solicitud'");
    }
});

function updateFechaUso(selectElement) { 
    const selectedOption = selectElement.options[selectElement.selectedIndex]; 
    const fechaReserva = selectedOption ? selectedOption.getAttribute('data-fecha') : ''; 
    if (fechaReserva) { 
        const regexFecha = /(\d{1,2}) de (\w+) de (\d{4})/; 
        const meses = { 'enero': '01',
                        'febrero': '02',
                        'marzo': '03', 
                        'abril': '04', 
                        'mayo': '05', 
                        'junio': '06', 
                        'julio': '07', 
                        'agosto': '08', 
                        'septiembre': '09', 
                        'octubre': '10', 
                        'noviembre': '11', 
                        'diciembre': '12' }; 
        const match = fechaReserva.match(regexFecha);
         if (match) { 
            const dia = match[1]; 
            const mes = meses[match[2].toLowerCase()];
            const anio = match[3];
            const formattedDate = `${anio}-${mes}-${dia.padStart(2, '0')}`;
             document.getElementById("fecha_uso").value = formattedDate;
             document.getElementById("hidden_fecha_uso").value = formattedDate;
             } else { console.error("Fecha inválida:", fechaReserva);             
              }
             }
             }
            
function actualizarSubcategorias() {
    const categoriaId = document.getElementById('categoria').value;
    console.log("ID de categoría seleccionado:", categoriaId);

    if (!categoriaId) {
        console.error("Falta el ID de categoría");
        return;
    }

    // Habilitar el selector de subcategorías después de seleccionar una categoría
    document.getElementById('subcategoria').disabled = false;

    fetch(`/appGestionLaboratorios/obtener_subcategorias/${categoriaId}/?nocache=${new Date().getTime()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const subcategoriaSelect = document.getElementById('subcategoria');
            subcategoriaSelect.innerHTML = '<option value="">Seleccione una subcategoría</option>'; // Limpiar opciones anteriores

            data.subcategorias.forEach(subcategoria => {
                const option = document.createElement('option');
                option.value = subcategoria.id_subcategoria;
                option.textContent = subcategoria.nombre;
                subcategoriaSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error al obtener las subcategorías:', error);
        });
}

function actualizarItems() {
    const categoriaId = document.getElementById('categoria').value;
    const subcategoriaId = document.getElementById('subcategoria').value;

    console.log("ID de categoría seleccionado:", categoriaId);
    console.log("ID de subcategoría seleccionado:", subcategoriaId);

    if (!categoriaId || !subcategoriaId) {
        console.log("Faltan los IDs de categoría o subcategoría, no se puede actualizar los ítems.");
        return;  // No hacer nada si faltan los IDs
    }

    console.log(`URL: /appGestionLaboratorios/obtener_items/${categoriaId}/${subcategoriaId}/`);

    fetch(`/appGestionLaboratorios/obtener_items/${categoriaId}/${subcategoriaId}/?nocache=${new Date().getTime()}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        const itemSelect = document.getElementById('item');
        itemSelect.innerHTML = ''; // Limpiar opciones anteriores
        itemSelect.disabled = false; // Habilitar el selector de ítems

        data.items.forEach(item => {
            const option = document.createElement('option');
            option.value = item.id_inventario; // Usa id_inventario aquí
            option.textContent = `${item.nombre} - Disponible: ${item.cantidad_disponible}`;
            itemSelect.appendChild(option);
        });
    })
    .catch(error => console.error('Error al obtener los ítems:', error));
}
