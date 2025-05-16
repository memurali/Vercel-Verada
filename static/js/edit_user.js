document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("edit-user-form");
  const successBox = document.getElementById("success-msg");
  const errorBox = document.getElementById("error-msg");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);

    fetch("/user/update/", {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
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
              text: 'User updated successfully.',
              confirmButtonText: 'OK',
              allowOutsideClick: false,     // Prevent click outside
              allowEscapeKey: false,        // Prevent ESC key
              allowEnterKey: true           // Optional: allow Enter to confirm
          }).then((result) => {
              if (result.isConfirmed) {
                  window.location.href = '/dashboard/usermanagement/';
              }
          });
        } else {
          errorBox.textContent = data.message || "Update failed.";
          errorBox.style.display = "block";
          successBox.style.display = "none";
        }
      })
      .catch(() => {
        errorBox.textContent = "Unexpected server error.";
        errorBox.style.display = "block";
      });
  });
});
