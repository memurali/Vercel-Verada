document.getElementById("commodity-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const successBox = document.getElementById("success-box");
    const errorBox = document.getElementById("error-box");

    fetch("/commodities/update/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData,
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            successBox.innerText = data.message;
            successBox.style.display = "block";
            errorBox.style.display = "none";
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: data.message,
                confirmButtonText: 'OK',
                allowOutsideClick: false,     // Prevent click outside
                allowEscapeKey: false,        // Prevent ESC key
                allowEnterKey: true           // Optional: allow Enter to confirm
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/client/commodities/dashboard/';
                }
            });
        } else {
            errorBox.innerText = data.message;
            errorBox.style.display = "block";
            successBox.style.display = "none";
        }
    })
    .catch(() => {
        errorBox.innerText = "Unexpected error occurred.";
        errorBox.style.display = "block";
    });
});