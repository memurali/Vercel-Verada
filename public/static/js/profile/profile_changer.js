document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const inputs = form.querySelectorAll("input, select, textarea");
  
    function clearErrors() {
      inputs.forEach((input) => {
        const errorSpan = document.getElementById("error_" + input.name);
        if (errorSpan) errorSpan.innerText = "";
      });
    }
  
    function showError(name, message) {
      const errorSpan = document.getElementById("error_" + name);
      if (errorSpan) {
        errorSpan.innerText = message;
        errorSpan.style.display = "block";
      }
    }
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      clearErrors();
  
      const formData = new FormData(form);
      let isValid = true;
  
      const fields = ["first_name", "last_name", "email", "phone", "company_name", "company_address"];
  
      for (let field of fields) {
        const value = formData.get(field);
        if (!value || value.trim() === "") {
          showError(field, `${field.replace("_", " ")} is required.`);
          isValid = false;
        }
      }
  
      const email = formData.get("email");
      const phone = formData.get("phone");
  
      if (email && !/^\S+@\S+\.\S+$/.test(email)) {
        showError("email", "Enter a valid email address.");
        isValid = false;
      }
  
      if (phone && !/^\d{10}$/.test(phone)) {
        showError("phone", "Phone number must be 10 digits.");
        isValid = false;
      }
  
      if (!isValid) return;
  
      fetch("/profile/submit/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.success) {
            Swal.fire({
              icon: "success",
              title: "Success!",
              text: data.message,
              confirmButtonText: "OK",
            }).then(() => {
              window.location.href = "/profile/dashboard/";
            });
          } else {
            Swal.fire({
              icon: "error",
              title: "Error",
              text: data.message || "Something went wrong.",
            });
          }
        })
        .catch(() => {
          Swal.fire({
            icon: "error",
            title: "Error",
            text: "Server error. Please try again.",
          });
        });
    });
  });
  