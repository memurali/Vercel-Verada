document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("role-assign-form");
  const successBox = document.getElementById("role-success");
  const errorBox = document.getElementById("role-error");
  const userIdInput = document.getElementById("selected-user-id");
  const usernameText = document.getElementById("selected-username");

  // On "+" button click
  document.querySelectorAll(".add-role-button").forEach((btn) => {
    btn.addEventListener("click", function () {
      const userId = this.dataset.userId;
      const row = this.closest("tr");
      const username = row.querySelector("td:first-child").innerText;

      userIdInput.value = userId;
      usernameText.textContent = `User: ${username}`;

      // Clear checkboxes
      form
        .querySelectorAll("input[name='role_ids']")
        .forEach((chk) => (chk.checked = false));
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    fetch("/update-role/", {
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
            icon: "success",
            title: "Success!",
            text: "Role Updated successfully.",
            confirmButtonText: "OK",
            allowOutsideClick: false, // Prevent click outside
            allowEscapeKey: false, // Prevent ESC key
            allowEnterKey: true, // Optional: allow Enter to confirm
          }).then((result) => {
            if (result.isConfirmed) {
              window.location.href = "/user-roles/";
            }
          });
          // setTimeout(() => location.reload(), 1000);
        } else {
          errorBox.innerText = data.message || "Something went wrong.";
          errorBox.style.display = "block";
          successBox.style.display = "none";
        }
      })
      .catch(() => {
        errorBox.innerText = "Server error.";
        errorBox.style.display = "block";
      });
  });

  const input = document.getElementById("user-role-search-input");

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      form.submit();
    }
  });
});

function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  input.addEventListener("keyup", function () {
    const search = input.value.toLowerCase();
    for (const row of table.getElementsByTagName("tbody")[0].rows) {
      const text = row.innerText.toLowerCase();
      row.style.display = text.includes(search) ? "" : "none";
    }
  });
}

filterTable("user-role-search-input", "user-role-table");