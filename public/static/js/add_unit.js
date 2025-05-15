document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("unit-form");
  const successBox = document.getElementById("success-msg");
  const errorBox = document.getElementById("error-msg");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const unitName = document.getElementById("unit_name").value.trim();
    if (!unitName) {
      errorBox.textContent = "Unit name is required.";
      errorBox.style.display = "block";
      successBox.style.display = "none";
      return;
    }

    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    fetch("/commodities/unit/add/", {
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
              text: 'Unit added successfully.',
              confirmButtonText: 'OK',
              allowOutsideClick: false,     // Prevent click outside
              allowEscapeKey: false,        // Prevent ESC key
              allowEnterKey: true           // Optional: allow Enter to confirm
          }).then((result) => {
              if (result.isConfirmed) {
                  window.location.href = '/commodities/dashboard/';
              }
          });
        } else {
          errorBox.textContent = data.message;
          errorBox.style.display = "block";
          successBox.style.display = "none";
        }
      })
      .catch(() => {
        errorBox.textContent = "Server error.";
        errorBox.style.display = "block";
      });
  });
});
