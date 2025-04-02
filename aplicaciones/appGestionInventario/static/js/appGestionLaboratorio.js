document.addEventListener('DOMContentLoaded', function () {
    initCategoryHandlers();
    setupItemManagement();
});

function initCategoryHandlers() {
    try {
        document.addEventListener('change', function (event) {
            const target = event.target;

            if (target.classList.contains('categoria')) {
                actualizarSubcategorias(target);
            }

            if (target.classList.contains('subcategoria')) {
                actualizarItems(target);
            }

            if (target.name === 'solicitud') {
                updateFechaUso(target);
            }
        });
    } catch (error) {
        console.error('Error en initCategoryHandlers:', error);
    }
}

function setupItemManagement() {
    try {
        const container = document.getElementById('items-container');
        const addButton = document.getElementById('agregar-item');

        if (!container || !addButton) return;

        addButton.addEventListener('click', function () {
            const itemEntries = container.querySelectorAll('.item-entry');
            if (itemEntries.length === 0) return;

            const newItem = itemEntries[0].cloneNode(true);

            // Limpiar valores
            newItem.querySelectorAll('input, select').forEach((element) => {
                if (element.tagName === 'SELECT') {
                    element.selectedIndex = 0;
                } else {
                    element.value = '';
                }
            });

            // Actualizar eventos en selectores clonados
            newItem.querySelectorAll('.categoria, .subcategoria').forEach(select => {
                select.addEventListener('change', function () {
                    if (select.classList.contains('categoria')) {
                        actualizarSubcategorias(select);
                    } else if (select.classList.contains('subcategoria')) {
                        actualizarItems(select);
                    }
                });
            });

            // Agregar evento de eliminación
            const removeBtn = newItem.querySelector('.remove-item');
            if (removeBtn) {
                removeBtn.addEventListener('click', function () {
                    if (document.querySelectorAll('.item-entry').length > 1) {
                        this.closest('.item-entry').remove();
                    }
                });
            }

            container.appendChild(newItem);
        });

        // Configurar botón eliminar existente
        document.addEventListener('click', function (event) {
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
    const subcategoriaSelect = selectElement.closest('.item-entry').querySelector('.subcategoria');

    if (!categoriaId) {
        subcategoriaSelect.innerHTML = '<option value="">Seleccione una subcategoría</option>';
        return;
    }

    fetch(`/appGestionLaboratorios/obtener_subcategorias/${categoriaId}/?nocache=${Date.now()}`)
        .then(response => response.json())
        .then(data => {
            subcategoriaSelect.innerHTML = '<option value="">Seleccione una subcategoría</option>';
            data.subcategorias.forEach(subcategoria => {
                const option = document.createElement('option');
                option.value = subcategoria.id_subcategoria;
                option.textContent = subcategoria.nombre;
                subcategoriaSelect.appendChild(option);
            });
            subcategoriaSelect.disabled = false;
        })
        .catch(error => console.error('Error al obtener subcategorías:', error));
}

function actualizarItems(selectElement) {
    const itemEntry = selectElement.closest('.item-entry');
    const categoriaElement = itemEntry.querySelector('.categoria');
    const subcategoriaElement = itemEntry.querySelector('.subcategoria');
    const itemSelect = itemEntry.querySelector('.item');

    if (!categoriaElement || !subcategoriaElement) return;

    const categoriaId = categoriaElement.value;
    const subcategoriaId = subcategoriaElement.value;

    if (!categoriaId || !subcategoriaId) {
        itemSelect.innerHTML = '<option value="">Seleccione un ítem</option>';
        return;
    }

    fetch(`/appGestionLaboratorios/obtener_items/${categoriaId}/${subcategoriaId}/?nocache=${Date.now()}`)
        .then(response => response.json())
        .then(data => {
            itemSelect.innerHTML = '<option value="">Seleccione un ítem</option>';
            data.items.forEach(item => {
                const option = document.createElement('option');
                option.value = item.id_inventario;
                option.textContent = `${item.nombre} - Disponible: ${item.cantidad_disponible} ${item.unidad_medida}`;
                itemSelect.appendChild(option);
            });
            itemSelect.disabled = false;
        })
        .catch(error => console.error('Error al obtener los ítems:', error));
}
