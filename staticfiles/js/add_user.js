document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("user-form");
  const successBox = document.getElementById("success-message");
  const errorBox = document.getElementById("error-message");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    const email = document.getElementById("user-email").value;
    const phone = document.getElementById("user-phoneno").value;

    const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    const phoneValid = /^\d{10}$/.test(phone);

    document.getElementById("emailError").style.display = emailValid
      ? "none"
      : "block";
    document.getElementById("phonenoError").style.display = phoneValid
      ? "none"
      : "block";

    if (!emailValid || !phoneValid) return;

    fetch("/ajax-create/", {
      method: "POST",
      headers: {
        "X-CSRFToken": csrfToken,
      },
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
              text: 'User added successfully.',
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
          errorBox.style.display = "block";
          errorBox.innerText = data.message;
          successBox.style.display = "none";
        }
      })
      .catch((err) => {
        errorBox.style.display = "block";
        errorBox.innerText = "Unexpected error occurred.";
        successBox.style.display = "none";
      });
  });
});
