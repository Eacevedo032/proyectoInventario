document.addEventListener('DOMContentLoaded', function () {

    console.log('Script cargado');

    // Habilitar/deshabilitar campos según selección
    document.querySelectorAll('.item').forEach(select => {
        select.addEventListener('change', function() {
            const itemEntry = this.closest('.item-entry');
            const cantidadInput = itemEntry.querySelector('input[name="cantidad_utilizada[]"]');
            const unidadDisplay = itemEntry.querySelector('.unidad-display');
            const unidadValue = itemEntry.querySelector('.unidad-value');
            
            if (this.value) {
                const selectedOption = this.options[this.selectedIndex];
                const maxCantidad = parseFloat(selectedOption.dataset.cantidad);
                const unidad = selectedOption.dataset.unidad || 'un';
                
                cantidadInput.disabled = false;
                cantidadInput.max = maxCantidad;
                cantidadInput.placeholder = `Máx: ${maxCantidad}`;
                
                if (unidadDisplay) unidadDisplay.value = unidad;
                if (unidadValue) unidadValue.value = unidad;
            } else {
                cantidadInput.disabled = true;
                cantidadInput.value = '';
                if (unidadDisplay) unidadDisplay.value = '';
                if (unidadValue) unidadValue.value = '';
            }
        });
    });

    initCategoryHandlers();
    setupItemManagement();
});

function initCategoryHandlers() {
    try {
        // Configurar eventos para selects existentes al cargar la página
        document.querySelectorAll('.categoria').forEach(select => {
            select.addEventListener('change', function() {
                actualizarSubcategorias(this);
            });
        });

        document.querySelectorAll('.subcategoria').forEach(select => {
            select.addEventListener('change', function() {
                actualizarItems(this);
            });
        });

        // Configurar evento para el select de solicitud
        const solicitudSelect = document.querySelector('select[name="solicitud"]');
        if (solicitudSelect) {
            solicitudSelect.addEventListener('change', function() {
                updateFechaUso(this);
            });
        }
    } catch (error) {
        console.error('Error en initCategoryHandlers:', error);
    }
}

function setupItemManagement() {
    try {
        const container = document.getElementById('items-container');
        const addButton = document.getElementById('agregar-item');

        if (!container || !addButton) return;

        // Configurar botón para agregar nuevos items
        addButton.addEventListener('click', function() {
            const itemEntries = container.querySelectorAll('.item-entry');
            if (itemEntries.length === 0) return;

            const firstItem = itemEntries[0];
            const newItem = firstItem.cloneNode(true);

            // Limpiar valores en el nuevo item
            newItem.querySelectorAll('input, select').forEach(element => {
                if (element.tagName === 'SELECT') {
                    element.selectedIndex = 0;
                    // Habilitar/deshabilitar según corresponda
                    if (element.classList.contains('subcategoria')) {
                        element.disabled = true;
                    }
                    if (element.classList.contains('item')) {
                        element.disabled = true;
                    }
                } else {
                    element.value = '';
                }
            });

            // Configurar eventos para los nuevos selects
            newItem.querySelector('.categoria').addEventListener('change', function() {
                actualizarSubcategorias(this);
            });

            newItem.querySelector('.subcategoria').addEventListener('change', function() {
                actualizarItems(this);
            });

            // Configurar botón de eliminar
            const removeBtn = newItem.querySelector('.remove-item');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    if (document.querySelectorAll('.item-entry').length > 1) {
                        this.closest('.item-entry').remove();
                    }
                });
            }

            container.appendChild(newItem);
        });

        // Configurar botones eliminar existentes
        document.addEventListener('click', function(event) {
            if (event.target.classList.contains('remove-item')) {
                if (document.querySelectorAll('.item-entry').length > 1) {
                    event.target.closest('.item-entry').remove();
                }
            }
        });
    } catch (error) {
        console.error('Error en setupItemManagement:', error);
    }
}

function updateFechaUso(selectElement) {
    const selectedOption = selectElement.options[selectElement.selectedIndex];
    const fechaReserva = selectedOption ? selectedOption.getAttribute('data-fecha') : '';

    if (!fechaReserva) return;

    const regexFecha = /(\d{1,2}) de (\w+) de (\d{4})/;
    const meses = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04', 'mayo': '05', 'junio': '06',
        'julio': '07', 'agosto': '08', 'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    };

    const match = fechaReserva.match(regexFecha);
    if (match) {
        const dia = match[1].padStart(2, '0');
        const mes = meses[match[2].toLowerCase()];
        const anio = match[3];
        const formattedDate = `${anio}-${mes}-${dia}`;

        document.getElementById("fecha_uso").value = formattedDate;
        document.getElementById("hidden_fecha_uso").value = formattedDate;
    } else {
        console.error("Fecha inválida:", fechaReserva);
    }
}

function actualizarSubcategorias(selectElement) {
    const categoriaId = selectElement.value;
    const itemEntry = selectElement.closest('.item-entry');
    const subcategoriaSelect = itemEntry.querySelector('.subcategoria');
    const itemSelect = itemEntry.querySelector('.item');
    
    // Resetear selects dependientes
    subcategoriaSelect.innerHTML = '<option value="">Seleccione subcategoría</option>';
    subcategoriaSelect.disabled = true;
    
    itemSelect.innerHTML = '<option value="">Seleccione ítem</option>';
    itemSelect.disabled = true;
    
    if (!categoriaId) return;
    
    // Mostrar loading
    const originalHTML = subcategoriaSelect.innerHTML;
    subcategoriaSelect.innerHTML = '<option value="">Cargando...</option>';
    
    fetch(`/appGestionLaboratorios/obtener_subcategorias/${categoriaId}/`)
        .then(response => {
            if (!response.ok) throw new Error('Error en la respuesta del servidor');
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') throw new Error(data.message);
            
            subcategoriaSelect.innerHTML = '<option value="">Seleccione subcategoría</option>';
            
            if (data.subcategorias && data.subcategorias.length > 0) {
                data.subcategorias.forEach(subcat => {
                    subcategoriaSelect.innerHTML += `
                        <option value="${subcat.id}">
                            ${subcat.nombre}
                        </option>`;
                });
                subcategoriaSelect.disabled = false;
            } else {
                subcategoriaSelect.innerHTML += '<option value="" disabled>No hay subcategorías disponibles</option>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            subcategoriaSelect.innerHTML = originalHTML;
            alert(`Error al cargar subcategorías: ${error.message}`);
        });
}

function actualizarItems(selectElement) {
    const subcategoriaId = selectElement.value;
    const itemEntry = selectElement.closest('.item-entry');
    const categoriaSelect = itemEntry.querySelector('.categoria');
    const itemSelect = itemEntry.querySelector('.item');
    const categoriaId = categoriaSelect.value;

    console.log('categoriaId:', categoriaId);
    console.log('subcategoriaId:', subcategoriaId);  // Asegúrate de que este valor no sea undefined

    // Resetear select de items
    itemSelect.innerHTML = '<option value="">Seleccione ítem</option>';
    itemSelect.disabled = true;

    if (!subcategoriaId || !categoriaId) {
        console.log("Subcategoría o categoría no seleccionada");
        return;
    }

    // Mostrar loading
    const originalHTML = itemSelect.innerHTML;
    itemSelect.innerHTML = '<option value="">Cargando...</option>';

    fetch(`/appGestionLaboratorios/obtener_items/?categoria_id=${categoriaId}&subcategoria_id=${subcategoriaId}`)
        .then(response => {
            if (!response.ok) throw new Error('Error en la respuesta del servidor');
            return response.json();
        })
        .then(data => {
            if (data.status === 'error') throw new Error(data.message);

            itemSelect.innerHTML = '<option value="">Seleccione ítem</option>';

            if (data.items && data.items.length > 0) {
                data.items.forEach(item => {
                    const unidad = item.unidad_medida__abreviatura || item.unidad_medida__nombre || 'un';
                    const infoExtra = [];
                    if (item.codigo) infoExtra.push(`Código: ${item.codigo}`);
                    if (item.num_serie) infoExtra.push(`Serie: ${item.num_serie}`);

                    const infoText = infoExtra.length > 0 ? ` (${infoExtra.join(' | ')})` : '';

                    itemSelect.innerHTML += `
                        <option value="${item.id}"
                                data-cantidad="${item.cantidad_disponible}"
                                data-unidad="${unidad}">
                            ${item.nombre} - Disp: ${item.cantidad_disponible} ${unidad}${infoText}
                        </option>`;
                });
                itemSelect.disabled = false;
            } else {
                itemSelect.innerHTML += '<option value="" disabled>No hay ítems disponibles</option>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            itemSelect.innerHTML = originalHTML;
            alert(`Error al cargar ítems: ${error.message}`);
        });
}
