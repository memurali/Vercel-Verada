document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('edit-roles-form');
    const errorMessage = document.getElementById('error-message');
    const roleId = document.getElementById('Roles_id').value;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const RoleName = document.getElementById('role_name').value.trim();

        errorMessage.style.display = 'none';

        if (!RoleName) {
            errorMessage.textContent = 'ROle Name and Code are required.';
            errorMessage.style.display = 'block';
            return;
        }

        fetch(`/roles/update/${roleId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({
                role_name: RoleName,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Role updated successfully!',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,     // Prevent click outside
                    allowEscapeKey: false,        // Prevent ESC key
                    allowEnterKey: true           // Optional: allow Enter to confirm
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/roles/type/';
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
