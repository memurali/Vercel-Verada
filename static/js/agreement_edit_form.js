document.getElementById("agreement-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const errorBox = document.getElementById("error-box");
    const successBox = document.getElementById("success-box");

    fetch("/agreements/update/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            successBox.innerText = data.message || "Agreement updated successfully!";
            successBox.style.display = "block";
            errorBox.style.display = "none";
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Agreement updated successfully.',
                confirmButtonText: 'OK',
                allowOutsideClick: false,     // Prevent click outside
                allowEscapeKey: false,        // Prevent ESC key
                allowEnterKey: true           // Optional: allow Enter to confirm
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/agreements/dashboard/';
                }
            });
        } else {
            errorBox.innerText = data.message || "Failed to update agreement.";
            errorBox.style.display = "block";
            successBox.style.display = "none";
        }
    })
    .catch(() => {
        errorBox.innerText = "Server error. Please try again.";
        errorBox.style.display = "block";
    });
});
