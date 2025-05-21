document.addEventListener('DOMContentLoaded', function () {
    console.log('Script cargado');

    // Validación del formulario antes de enviar
    const formProductos = document.getElementById('form-productos');
    if (formProductos) {
        formProductos.addEventListener('submit', function (e) {
            const itemEntries = document.querySelectorAll('.item-entry');
            const hasValidItems = Array.from(itemEntries).some(entry => {
                const productoId = entry.querySelector('.producto-id')?.value;
                const cantidad = entry.querySelector('input[name="cantidad_utilizada[]"]')?.value;
                return productoId && cantidad;
            });

            if (!hasValidItems) {
                e.preventDefault();
                alert('Debe agregar y completar al menos un producto válido');
            }
        });
    }

    // Configurar eventos iniciales
    setupItemManagement();

    // Configurar búsqueda para items existentes al cargar
    document.querySelectorAll('.buscar-producto').forEach(input => {
        const resultadosContainer = input.nextElementSibling;
        const productIdInput = input.parentElement.querySelector('.producto-id');
        if (input && resultadosContainer && productIdInput) {
            input.addEventListener('input', function() {
                handleProductSearch(this, resultadosContainer, productIdInput);
            });
        }
    });
});

function setupItemManagement() {
    try {
        const container = document.getElementById('items-container');
        const addButton = document.getElementById('agregar-item');

        if (!container || !addButton) return;

        // ✅ Configurar botón para agregar nuevos items
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

            // ✅ Configurar eventos de búsqueda si hay input de producto
            const buscarInput = newItem.querySelector('.buscar-producto');
            const resultadosContainer = buscarInput?.nextElementSibling;
            const productIdInput = newItem.querySelector('.producto-id');

            if (buscarInput && resultadosContainer && productIdInput) {
                buscarInput.addEventListener('input', function () {
                    handleProductSearch(this, resultadosContainer, productIdInput);
                });
            }

            // ✅ Configurar eventos para los nuevos selects
            const categoriaSelect = newItem.querySelector('.categoria');
            if (categoriaSelect) {
                categoriaSelect.addEventListener('change', function () {
                    actualizarSubcategorias(this);
                });
            }

            const subcategoriaSelect = newItem.querySelector('.subcategoria');
            if (subcategoriaSelect) {
                subcategoriaSelect.addEventListener('change', function () {
                    actualizarItems(this);
                });
            }

            // ✅ Configurar botón de eliminar
            const removeBtn = newItem.querySelector('.remove-item');
            if (removeBtn) {
                removeBtn.addEventListener('click', function() {
                    if (document.querySelectorAll('.item-entry').length > 1) {
                        this.closest('.item-entry').remove();
                    }
                });
            }

            // Agregar el nuevo item al contenedor
            container.appendChild(newItem);
        });

        // ✅ Configurar botones eliminar existentes
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


function handleProductSearch(inputElement, resultsContainer, idInput) {
    const searchTerm = inputElement.value.trim();
    
    if (searchTerm.length < 2) {
        if (resultsContainer) resultsContainer.style.display = 'none';
        return;
    }

    fetch('/appGestionLaboratorios/obtener_items/?search=' + encodeURIComponent(searchTerm))
        .then(response => {
            if (!response.ok) throw new Error('Error en la respuesta');
            return response.json();
        })
        .then(data => {
            if (!resultsContainer) return;
            
            resultsContainer.innerHTML = '';
            
            if (data.status === 'success' && data.items.length > 0) {
                data.items.forEach(item => {
                    const div = document.createElement('div');
                    div.classList.add('resultado-item');
                    div.textContent = `${item.nombre} (Disponible: ${item.cantidad_disponible} ${item.unidad_medida})`;

                    div.addEventListener('click', function () {
    const itemEntry = inputElement.closest('.item-entry');

    const productoIdInput = itemEntry.querySelector('.producto-id');
    const cantidadInput = itemEntry.querySelector('input[name="cantidad_utilizada[]"]');
    const unidadSelect = itemEntry.querySelector('select[name="unidad_medida[]"]');

    inputElement.value = item.nombre;

    if (productoIdInput) productoIdInput.value = item.id;
    if (unidadSelect) unidadSelect.value = item.unidad_medida;
    if (cantidadInput) {
        cantidadInput.disabled = false;
        cantidadInput.placeholder = `Máx: ${item.cantidad_disponible}`;
        cantidadInput.max = item.cantidad_disponible;
    }

    resultsContainer.style.display = 'none';
});


                    resultsContainer.appendChild(div);
                });
                resultsContainer.style.display = 'block';
            } else {
                resultsContainer.innerHTML = '<div class="resultado-item">No se encontraron productos</div>';
                resultsContainer.style.display = 'block';
            }
        })
        .catch(error => {
            console.error('Error al buscar productos:', error);
            if (resultsContainer) resultsContainer.style.display = 'none';
        });
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
