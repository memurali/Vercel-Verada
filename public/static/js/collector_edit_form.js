document.getElementById("collector-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const errorBox = document.getElementById("collector-error");
    const successBox = document.getElementById("collector-success");

    const formData = new FormData(form);
    const id = form.getAttribute("data-id");

    fetch(`/collectors/update/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        },
        body: formData,
    })
    .then((res) => res.json())
    .then((data) => {
        if (data.success) {
            successBox.style.display = "block";
            errorBox.style.display = "none";
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Waste collector updated successfully.',
                confirmButtonText: 'OK',
                allowOutsideClick: false,     // Prevent click outside
                allowEscapeKey: false,        // Prevent ESC key
                allowEnterKey: true           // Optional: allow Enter to confirm
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/collectors/dashboard/';
                }
            });
        } else {
            errorBox.innerText = data.message;
            errorBox.style.display = "block";
            successBox.style.display = "none";
        }
    })
    .catch(() => {
        errorBox.innerText = "Unexpected server error.";
        errorBox.style.display = "block";
    });
});
