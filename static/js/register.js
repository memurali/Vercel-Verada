const AJAX_REGISTER_URL = "/api/auth/ajax-register/";

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function validatePhone(phone) {
    return /^[0-9]{10}$/.test(phone);
}  

function submitRegister(e) {
  e.preventDefault();

  const form = document.getElementById("register-form");
  const name = form.name.value.trim();
  const email = form.email.value.trim();
  const phone = form.phone.value.trim();

  const successBox = document.getElementById("register-success");
  const errorBox = document.getElementById("register-error");

  if (!name || !email || !phone) {
    errorBox.innerText = "All fields are required.";
    errorBox.style.display = "block";
    successBox.style.display = "none";
    return false;
  }

  if (!validateEmail(email)) {
    errorBox.innerText = "Invalid email format.";
    errorBox.style.display = "block";
    return false;
  }

  if (!validatePhone(phone)) {
    errorBox.innerText = "Phone must be exactly 10 digits, no spaces or symbols.";
    errorBox.style.display = "block";
    return false;
  }

  fetch(AJAX_REGISTER_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
    body: JSON.stringify({ name, email, phone }),
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        successBox.style.display = "block";
        errorBox.style.display = "none";
        form.reset();
      } else {
        errorBox.textContent = data.message || "Registration failed.";
        errorBox.style.display = "block";
        successBox.style.display = "none";
      }
    })
    .catch(() => {
      errorBox.textContent = "Server error.";
      errorBox.style.display = "block";
      successBox.style.display = "none";
    });

  return false;
}
