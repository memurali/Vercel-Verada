document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("collector-form");
    const errorBox = document.getElementById("error-box");
    const successBox = document.getElementById("success-box");
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(form);
  
      fetch("/collectors/create/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          successBox.style.display = "block";
          errorBox.style.display = "none";
          form.reset();
        } else {
          errorBox.innerText = data.message || "Error occurred";
          errorBox.style.display = "block";
          successBox.style.display = "none";
        }
      })
      .catch(() => {
        errorBox.innerText = "Server error";
        errorBox.style.display = "block";
      });
    });
});
  