    //  app/static/js/cat.js 
    
// scripts para cat mantenimiento
    // Cambio de tema
    // document.addEventListener('DOMContentLoaded', () => {
    //     const themeBtn = document.getElementById('themeDropdown');
    //     const themeIcon = themeBtn.querySelector('i');
        
    //     // Cargar tema guardado
    //     const savedTheme = localStorage.getItem('theme') || 'dark';
    //     document.documentElement.setAttribute('data-theme', savedTheme);
        
    //     // Actualizar icono según tema
    //     if (savedTheme === 'dark') {
    //         themeIcon.classList.remove('bi-sun');
    //         themeIcon.classList.add('bi-moon-stars');
    //     } else {
    //         themeIcon.classList.remove('bi-moon-stars');
    //         themeIcon.classList.add('bi-sun');
    //     }
        
    //     // Evento para cambiar tema
    //     themeBtn.addEventListener('click', () => {
    //         const currentTheme = document.documentElement.getAttribute('data-theme');
    //         const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
    //         document.documentElement.setAttribute('data-theme', newTheme);
    //         localStorage.setItem('theme', newTheme);
            
    //         if (newTheme === 'dark') {
    //             themeIcon.classList.remove('bi-sun');
    //             themeIcon.classList.add('bi-moon-stars');
    //         } else {
    //             themeIcon.classList.remove('bi-moon-stars');
    //             themeIcon.classList.add('bi-sun');
    //         }
            
    //         showAlert(`Tema cambiado a ${newTheme === 'dark' ? 'oscuro' : 'claro'}`, 'success');
    //     });
        
    //     // Vista previa de imagen
    //     const imageInput = document.querySelector('input[type="url"], input[type="file"]');
    //     const imagePreview = document.getElementById('imagePreview');
    //     const previewText = document.getElementById('previewText');
        
    //     function updateImagePreview() {
    //         const urlInput = document.querySelector('#url input');
    //         const fileInput = document.querySelector('#upload input[type="file"]');
            
    //         if (urlInput.value && urlInput.checkValidity()) {
    //             imagePreview.src = urlInput.value;
    //             imagePreview.style.display = 'block';
    //             previewText.style.display = 'none';
    //         } else if (fileInput.files && fileInput.files[0]) {
    //             const reader = new FileReader();
    //             reader.onload = function(e) {
    //                 imagePreview.src = e.target.result;
    //                 imagePreview.style.display = 'block';
    //                 previewText.style.display = 'none';
    //             }
    //             reader.readAsDataURL(fileInput.files[0]);
    //         } else {
    //             imagePreview.style.display = 'none';
    //             previewText.style.display = 'block';
    //         }
    //     }
        
    //     // Eventos para inputs de imagen
    //     document.querySelector('#url input').addEventListener('input', updateImagePreview);
    //     document.querySelector('#upload input[type="file"]').addEventListener('change', updateImagePreview);
        
    //     // Cambiar entre pestañas de imagen
    //     document.querySelectorAll('#imageTab button').forEach(tab => {
    //         tab.addEventListener('click', () => {
    //             setTimeout(updateImagePreview, 100);
    //         });
    //     });
        
    //     // Función para mostrar alertas
    //     function showAlert(message, type) {
    //         const alertContainer = document.querySelector('.alert-container');
    //         const alertId = 'alert-' + Date.now();
            
    //         const alert = document.createElement('div');
    //         alert.className = `alert alert-${type} alert-dismissible fade show`;
    //         alert.role = 'alert';
    //         alert.innerHTML = `
    //             ${message}
    //             <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    //         `;
            
    //         alertContainer.appendChild(alert);
            
    //         // Eliminar alerta después de 5 segundos
    //         setTimeout(() => {
    //             alert.classList.remove('show');
    //             setTimeout(() => {
    //                 alert.remove();
    //             }, 300);
    //         }, 5000);
    //     }
        
    //     // Evento de ejemplo para eliminar producto
    //     document.querySelectorAll('.btn-outline-danger').forEach(button => {
    //         button.addEventListener('click', function() {
    //             if (confirm('¿Estás seguro de eliminar este producto? Esta acción no se puede deshacer.')) {
    //                 const row = this.closest('tr');
    //                 row.classList.add('table-danger');
    //                 setTimeout(() => {
    //                     row.style.opacity = '0.5';
    //                 }, 300);
                    
    //                 showAlert('Producto eliminado correctamente', 'success');
    //             }
    //         });
    //     });
        
    //     // Evento de ejemplo para eliminar imagen
    //     document.querySelectorAll('.image-card .btn-danger').forEach(button => {
    //         button.addEventListener('click', function() {
    //             if (confirm('¿Estás seguro de eliminar esta imagen?')) {
    //                 const card = this.closest('.image-card');
    //                 card.classList.add('border-danger');
    //                 this.innerHTML = '<i class="bi bi-trash me-1"></i> Eliminando...';
    //                 this.disabled = true;
                    
    //                 setTimeout(() => {
    //                     card.remove();
    //                     showAlert('Imagen eliminada correctamente', 'success');
    //                 }, 1000);
    //             }
    //         });
    //     });
        
    //     // Ejemplo de alerta de guardado exitoso
    //     setTimeout(() => {
    //         showAlert('Cambios guardados correctamente', 'success');
    //     }, 2000);
    // });
        // scripts para sincronizar catalogo
    // Cambiador de tema
            document.addEventListener('DOMContentLoaded', () => {
                const themeDropdown = document.getElementById('themeDropdown');
                themeDropdown.addEventListener('click', () => {
                    const currentTheme = document.documentElement.getAttribute('data-theme');
                    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                    
                    document.documentElement.setAttribute('data-theme', newTheme);
                    localStorage.setItem('theme', newTheme);
                    
                    // Actualizar icono
                    const icon = themeDropdown.querySelector('i');
                    icon.className = newTheme === 'dark' ? 'bi bi-moon-stars' : 'bi bi-sun';
                });
                
                // Manejar selección de productos
                const masterCheckbox = document.getElementById('masterCheckbox');
                const productCheckboxes = document.querySelectorAll('.product-checkbox');
                const selectAllBtn = document.getElementById('selectAllBtn');
                const deselectAllBtn = document.getElementById('deselectAllBtn');
                const selectedCount = document.getElementById('selectedCount');
                const syncCount = document.getElementById('syncCount');
                
                function updateSelectedCount() {
                    const selected = document.querySelectorAll('.product-checkbox:checked').length;
                    selectedCount.textContent = selected;
                    syncCount.textContent = selected;
                }
                
                // Seleccionar/deseleccionar todos
                masterCheckbox.addEventListener('change', () => {
                    productCheckboxes.forEach(checkbox => {
                        checkbox.checked = masterCheckbox.checked;
                    });
                    updateSelectedCount();
                });
                
                selectAllBtn.addEventListener('click', () => {
                    productCheckboxes.forEach(checkbox => {
                        checkbox.checked = true;
                    });
                    masterCheckbox.checked = true;
                    updateSelectedCount();
                });
                
                deselectAllBtn.addEventListener('click', () => {
                    productCheckboxes.forEach(checkbox => {
                        checkbox.checked = false;
                    });
                    masterCheckbox.checked = false;
                    updateSelectedCount();
                });
                
                // Actualizar contador cuando cambian las selecciones individuales
                productCheckboxes.forEach(checkbox => {
                    checkbox.addEventListener('change', () => {
                        // Verificar si todos están seleccionados
                        const allChecked = [...productCheckboxes].every(cb => cb.checked);
                        masterCheckbox.checked = allChecked;
                        updateSelectedCount();
                    });
                });
                
                // Inicializar contador
                updateSelectedCount();
                
                // Simular búsqueda
                document.getElementById('searchButton').addEventListener('click', () => {
                    // Simular carga
                    const searchBtn = document.getElementById('searchButton');
                    const originalText = searchBtn.innerHTML;
                    searchBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Buscando...';
                    searchBtn.disabled = true;
                    
                    setTimeout(() => {
                        searchBtn.innerHTML = originalText;
                        searchBtn.disabled = false;
                        
                        // Mostrar mensaje de éxito
                        const toast = document.createElement('div');
                        toast.className = 'position-fixed bottom-0 end-0 p-3';
                        toast.style.zIndex = '11';
                        toast.innerHTML = `
                            <div class="toast show" role="alert">
                                <div class="toast-header bg-success text-white">
                                    <strong class="me-auto">Búsqueda completada</strong>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                                </div>
                                <div class="toast-body">
                                    Se encontraron 5 productos que coinciden con tu búsqueda.
                                </div>
                            </div>
                        `;
                        document.body.appendChild(toast);
                        
                        // Eliminar después de 3 segundos
                        setTimeout(() => {
                            toast.remove();
                        }, 3000);
                    }, 1500);
                });
                
                // Confirmar sincronización
                document.getElementById('confirmSync').addEventListener('click', () => {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('syncModal'));
                    modal.hide();
                    
                    // Simular sincronización
                    const syncBtn = document.getElementById('confirmSync');
                    const originalText = syncBtn.innerHTML;
                    syncBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Sincronizando...';
                    syncBtn.disabled = true;
                    
                    setTimeout(() => {
                        syncBtn.innerHTML = originalText;
                        syncBtn.disabled = false;
                        
                        // Mostrar mensaje de éxito
                        const toast = document.createElement('div');
                        toast.className = 'position-fixed bottom-0 end-0 p-3';
                        toast.style.zIndex = '11';
                        toast.innerHTML = `
                            <div class="toast show" role="alert">
                                <div class="toast-header bg-success text-white">
                                    <strong class="me-auto">Sincronización exitosa</strong>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast"></button>
                                </div>
                                <div class="toast-body">
                                    Los productos seleccionados se han sincronizado correctamente.
                                </div>
                            </div>
                        `;
                        document.body.appendChild(toast);
                        
                        // Eliminar después de 3 segundos
                        setTimeout(() => {
                            toast.remove();
                        }, 3000);
                    }, 2000);
                });
            });

            // scripts para alta catalogo
            // Selector de temas
        document.addEventListener('DOMContentLoaded', () => {
            // Cargar tema desde localStorage
            const savedTheme = localStorage.getItem('theme') || 'dark';
            document.documentElement.setAttribute('data-theme', savedTheme);
            
            // Actualizar ícono según tema
            updateThemeIcon(savedTheme);

            // Configurar el selector de temas
            document.getElementById('themeDropdown').addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // Actualizar ícono
                updateThemeIcon(newTheme);
            });
            
            // Gestión de imágenes
            setupImageHandling();
            
            // Validación de formulario
            document.getElementById('productForm').addEventListener('submit', function(e) {
                e.preventDefault();
                if (validateForm()) {
                    showSuccessAlert('Producto guardado correctamente.');
                }
            });
            
            // Botón de borrador
            document.getElementById('saveDraftBtn').addEventListener('click', function() {
                if (validateForm(true)) {
                    showWarningAlert('Producto guardado como borrador, no visible en el catálogo.');
                }
            });
        });
        
        function updateThemeIcon(theme) {
            const icon = document.querySelector('#themeDropdown i');
            icon.className = theme === 'dark' ? 'bi bi-moon-stars' : 'bi bi-sun';
        }
        
        function setupImageHandling() {
            const imagePreview = document.getElementById('imagePreview');
            const imageList = document.getElementById('imageList');
            const fileInput = document.getElementById('fileInput');
            const uploadBtn = document.getElementById('uploadBtn');
            const addUrlBtn = document.getElementById('addUrlBtn');
            const imageUrl = document.getElementById('imageUrl');
            
            // Abrir selector de archivos al hacer clic en el botón
            uploadBtn.addEventListener('click', () => fileInput.click());
            
            // Manejar selección de archivos
            fileInput.addEventListener('change', handleFileSelect);
            
            // Permitir arrastrar y soltar
            imagePreview.addEventListener('dragover', (e) => {
                e.preventDefault();
                imagePreview.classList.add('active');
            });
            
            imagePreview.addEventListener('dragleave', () => {
                imagePreview.classList.remove('active');
            });
            
            imagePreview.addEventListener('drop', (e) => {
                e.preventDefault();
                imagePreview.classList.remove('active');
                
                if (e.dataTransfer.files.length) {
                    handleFiles(e.dataTransfer.files);
                }
            });
            
            // Agregar imagen desde URL
            addUrlBtn.addEventListener('click', () => {
                const url = imageUrl.value.trim();
                if (url && isValidImageUrl(url)) {
                    addImageToList(url);
                    imageUrl.value = '';
                } else {
                    alert('Por favor ingresa una URL válida de imagen (jpg, png)');
                }
            });
        }
        
        function handleFileSelect(e) {
            handleFiles(e.target.files);
        }
        
        function handleFiles(files) {
            for (let i = 0; i < files.length; i++) {
                const file = files[i];
                
                // Validar tipo y tamaño
                if (!isValidImage(file)) {
                    alert(`El archivo ${file.name} no es válido. Solo se permiten JPG/PNG de menos de 2MB.`);
                    continue;
                }
                
                // Crear vista previa
                const reader = new FileReader();
                reader.onload = function(e) {
                    addImageToList(e.target.result, file.name);
                };
                reader.readAsDataURL(file);
            }
        }
        
        function isValidImage(file) {
            const validTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            const maxSize = 2 * 1024 * 1024; // 2MB
            
            return validTypes.includes(file.type) && file.size <= maxSize;
        }
        
        function isValidImageUrl(url) {
            return /\.(jpeg|jpg|png)$/i.test(url);
        }
        
        function addImageToList(src, name = 'Imagen') {
            const id = 'img-' + Date.now();
            const imageItem = document.createElement('div');
            imageItem.className = 'col-md-3 image-item';
            imageItem.innerHTML = `
                <div class="card">
                    <div class="card-body p-2">
                        <div class="preview-container">
                            <img src="${src}" class="img-fluid rounded" alt="${name}">
                            <div class="remove-btn" data-id="${id}">
                                <i class="bi bi-x"></i>
                            </div>
                        </div>
                        <div class="d-flex justify-content-between mt-2">
                            <span class="small text-truncate">${name}</span>
                            <span class="drag-handle"><i class="bi bi-grip-horizontal"></i></span>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('imageList').appendChild(imageItem);
            
            // Agregar evento para eliminar imagen
            imageItem.querySelector('.remove-btn').addEventListener('click', function() {
                this.closest('.image-item').remove();
            });
        }
        
        function validateForm(isDraft = false) {
            let isValid = true;
            const form = document.getElementById('productForm');
            
            // Validar campos obligatorios
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validar números positivos
            const numberFields = ['existencias', 'precio'];
            numberFields.forEach(id => {
                const field = document.getElementById(id);
                if (field.value && parseFloat(field.value) < 0) {
                    field.classList.add('is-invalid');
                    isValid = false;
                }
            });
            
            return isDraft ? true : isValid; // Los borradores pueden tener campos vacíos
        }
        
        function showSuccessAlert(message) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-success alert-dismissible fade show';
            alert.role = 'alert';
            alert.innerHTML = `
                <i class="bi bi-check-circle-fill me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('main').prepend(alert);
        }
        
        function showWarningAlert(message) {
            const alert = document.createElement('div');
            alert.className = 'alert alert-warning alert-dismissible fade show';
            alert.role = 'alert';
            alert.innerHTML = `
                <i class="bi bi-exclamation-triangle-fill me-2"></i>${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;
            
            document.querySelector('main').prepend(alert);
        }