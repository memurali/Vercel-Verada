document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("commodity-form");
  const successBox = document.getElementById("success-box");
  const errorBox = document.getElementById("error-box");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    fetch("/commodities/add/submit/", {
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
              text: 'Commodity added successfully.',
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
});
