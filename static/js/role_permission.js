document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("permission-form");
  const errorBox = document.getElementById("error-box");
  const successBox = document.getElementById("success-box");

  // Toggle module permission visibility
  document.querySelectorAll(".module-checkbox").forEach((checkbox, idx) => {
    checkbox.addEventListener("change", function () {
      const container = checkbox.closest(".module-container");
      const options = container.querySelector(".module-options");
      options.style.display = checkbox.checked ? "block" : "none";
    });
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    errorBox.style.display = "none";
    successBox.style.display = "none";

    const roleId = form.querySelector("select[name='role_id']").value;
    if (!roleId) {
      errorBox.innerText = "Please select a role.";
      errorBox.style.display = "block";
      return;
    }

    const moduleContainers = form.querySelectorAll(".module-container");
    let atLeastOneModuleChecked = false;
    let valid = true;

    moduleContainers.forEach((container) => {
      const moduleCheckbox = container.querySelector(".module-checkbox");
      const permissions = container.querySelectorAll(
        ".module-options input[type='checkbox']"
      );
      const anyPermissionChecked = Array.from(permissions).some(
        (p) => p.checked
      );

      if (moduleCheckbox.checked) {
        atLeastOneModuleChecked = true;

        if (!anyPermissionChecked) {
          valid = false;
          container.querySelector(".module-options").style.border =
            "1px solid red";
        } else {
          container.querySelector(".module-options").style.border = "none";
        }
      }
    });

    if (!atLeastOneModuleChecked) {
      errorBox.innerText = "Please select at least one module.";
      errorBox.style.display = "block";
      return;
    }

    if (!valid) {
      errorBox.innerText =
        "Each selected module must have at least one permission (Read, Write, Delete, No Access) selected.";
      errorBox.style.display = "block";
      return;
    }

    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    fetch("/permissions/assign/", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          successBox.style.display = "block";
          errorBox.style.display = "none";
          Swal.fire({
            icon: "success",
            title: "Success!",
            text: "Permission added to role successfully.",
            confirmButtonText: "OK",
            allowOutsideClick: false, // Prevent click outside
            allowEscapeKey: false, // Prevent ESC key
            allowEnterKey: true, // Optional: allow Enter to confirm
          }).then((result) => {
            if (result.isConfirmed) {
              window.location.href = "/dashboard/usermanagement/";
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
document.addEventListener("DOMContentLoaded", function () {
  const roleSelect = document.querySelector('select[name="role_id"]');
  roleSelect.addEventListener("change", function () {
    const roleId = this.value;

    if (!roleId) return;

    fetch(`/get-role-permissions/?role_id=${roleId}`)
      .then((response) => response.json())
      .then((data) => {
        if (!data.success) return;

        // Reset checkboxes
        document
          .querySelectorAll(".module-checkbox")
          .forEach((cb) => (cb.checked = false));
        document.querySelectorAll(".module-options").forEach((el) => {
          el.style.display = "none";
          el.querySelectorAll("input[type=checkbox]").forEach(
            (cb) => (cb.checked = false)
          );
        });

        for (const [moduleCode, actions] of Object.entries(data.permissions)) {
          const checkboxes = document.querySelectorAll(
            `input[name="${moduleCode}[]"]`
          );

          if (checkboxes.length) {
            // Enable module section
            const container = checkboxes[0].closest(".module-container");
            container.querySelector(".module-checkbox").checked = true;
            container.querySelector(".module-options").style.display = "block";

            // Check actions
            checkboxes.forEach((cb) => {
              if (actions.includes(cb.value)) cb.checked = true;
            });
          }
        }
      });
  });

  // Toggle module options
  document.querySelectorAll(".module-checkbox").forEach((cb) => {
    cb.addEventListener("change", function () {
      const options =
        this.closest(".module-container").querySelector(".module-options");
      options.style.display = this.checked ? "block" : "none";
    });
  });
});
