document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("waste-group-form");

  function toggleSections(selected) {
      const masterNew = document.getElementById("master_new");
      const masterExist = document.getElementById("master_exist");

      if (selected === "yes") {
          masterNew.style.display = "block";
          masterExist.style.display = "none";

          // Set required only for NEW fields
          form.querySelectorAll("#master_new input").forEach(input => {
              input.setAttribute("required", "required");
          });
          form.querySelectorAll("#master_exist input, #master_exist select").forEach(input => {
              input.removeAttribute("required");
          });

      } else if (selected === "no") {
          masterNew.style.display = "none";
          masterExist.style.display = "block";

          // Set required only for EXISTING fields
          form.querySelectorAll("#master_exist input, #master_exist select").forEach(input => {
              input.setAttribute("required", "required");
          });
          form.querySelectorAll("#master_new input").forEach(input => {
              input.removeAttribute("required");
          });
      }
  }

  document.querySelectorAll("input[name='source_master_cat']").forEach(radio => {
      radio.addEventListener("change", function () {
          toggleSections(this.value);
      });
  });

  // On page load
  const selected = document.querySelector("input[name='source_master_cat']:checked");
  if (selected) {
      toggleSections(selected.value);
  }

  form.addEventListener("submit", function (e) {
      e.preventDefault();

      const selectedOption = document.querySelector("input[name='source_master_cat']:checked");
      if (!selectedOption) {
          Swal.fire("Error", "Please select whether you want to add New or Existing group.", "error");
          return;
      }

      const formData = new FormData(form);
      const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

      fetch("/waste/submit/group/form/", {
          method: "POST",
          headers: {
              "X-CSRFToken": csrfToken
          },
          body: formData
      })
      .then(res => res.json())
      .then(data => {
          if (data.success) {
              Swal.fire({
                  icon: "success",
                  title: "Success!",
                  text: "Waste group saved successfully.",
                  confirmButtonText: "OK"
              }).then(() => {
                  window.location.href = "/waste/group/dashboard/";
              });
          } else {
              Swal.fire("Error", data.message || "Something went wrong.", "error");
          }
      })
      .catch((error) => {
          Swal.fire("Error", "Unexpected error occurred.", "error");
          console.error(error);
      });
  });

  const groupSelect = document.querySelector("select[name='waste_group_id']");
  const descriptionInput = document.querySelector("input[name='description_exist']");

  if (groupSelect) {
    groupSelect.addEventListener("change", function () {
      const selectedGroupId = this.value;

      if (!selectedGroupId) {
        descriptionInput.value = "";
        return;
      }

      fetch(`/waste/ajax/get-group-description/?group_id=${selectedGroupId}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            descriptionInput.value = data.description;
          } else {
            descriptionInput.value = "";
            console.warn(data.message || "No description found.");
          }
        })
        .catch(err => {
          console.error("Fetch error:", err);
          descriptionInput.value = "";
        });
    });
  }
});
