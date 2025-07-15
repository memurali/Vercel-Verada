document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('edit-collector_type-form');
    const errorMessage = document.getElementById('error-message');
    const collectorTypeId = document.getElementById('collector_type_id').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const CollectorType = document.getElementById('collector_type').value.trim();

        errorMessage.style.display = 'none';

        if (!CollectorType) {
            errorMessage.textContent = 'CollectorType are required.';
            errorMessage.style.display = 'block';
            return;
        }

        fetch(`/collectors/collectors_type/update/${collectorTypeId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                collector_type: CollectorType,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Collector Type updated successfully!',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,     // Prevent click outside
                    allowEscapeKey: false,        // Prevent ESC key
                    allowEnterKey: true           // Optional: allow Enter to confirm
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/collectors/collectors_type/type/';
                    }
                });
            } else {
                errorMessage.textContent = data.message || 'Something went wrong.';
                errorMessage.style.display = 'block';
            }
        })
        .catch(error => {
            errorMessage.textContent = 'Server Error. Please try again later.';
            errorMessage.style.display = 'block';
        });
    });
});
