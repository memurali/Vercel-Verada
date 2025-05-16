document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("collector_type_form");
    const successBox = document.getElementById("success-message");
    const errorBox = document.getElementById("error-message");
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(form);
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;
  
      fetch("/collectors/assign_collector_type_ajax/", {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            successBox.style.display = "block";
            errorBox.style.display = "none";
            form.reset();
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Collector Type added successfully.',
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
            errorBox.style.display = "block";
            errorBox.innerText = data.message || "Something went wrong.";
            successBox.style.display = "none";
          }
        })
        .catch(() => {
          errorBox.style.display = "block";
          errorBox.innerText = "Server error.";
          successBox.style.display = "none";
        });
    });
  });
  