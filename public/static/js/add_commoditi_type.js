document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('commodity-form');
    const errorMessage = document.getElementById('error-message');

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const commodityName = document.getElementById('commodity_name').value.trim();
        const commodityCode = document.getElementById('commodity_code').value.trim();
        const isActive = document.getElementById('active_status').checked;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        errorMessage.style.display = 'none';

        if (!commodityName || !commodityCode) {
            errorMessage.textContent = 'Commodity Name and Code are required.';
            errorMessage.style.display = 'block';
            return;
        }

        fetch('/commodities/create/type/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                commodity_name: commodityName,
                commodity_code: commodityCode,
                active_status: isActive ? 'A' : 'I',
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Commodity added successfully!',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,     // Prevent click outside
                    allowEscapeKey: false,        // Prevent ESC key
                    allowEnterKey: true           // Optional: allow Enter to confirm
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/commodities/type/dashboard/';
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
