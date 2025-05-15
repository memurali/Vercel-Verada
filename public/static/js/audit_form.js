document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("audit-form");
  const errorBox = document.getElementById("error-box");
  const successBox = document.getElementById("success-box");

  const auditTypeSelect = document.getElementById("auditType");
  const waiverCheckbox = document.getElementById("waiverCheckbox");
  const waiverTypeSection = document.getElementById("waiverTypeSection");

  const initialFields = document.getElementById("initialAuditFields");
  const verificationFields = document.getElementById("verificationAuditFields");

  // ✅ Define AFTER all variables are initialized
  function toggleCommoditySections() {
    const waiverApplied = waiverCheckbox.checked;
    const auditType = auditTypeSelect.value;

    if (waiverApplied) {
      initialFields.style.display = "none";
      verificationFields.style.display = "none";
    } else {
      initialFields.style.display = auditType === "initial" ? "block" : "none";
      verificationFields.style.display =
        auditType === "verification" ? "block" : "none";
    }
  }

  // ✅ Event listeners using toggleCommoditySections AFTER it's declared
  if (waiverCheckbox) {
    waiverCheckbox.addEventListener("change", function () {
      waiverTypeSection.style.display = this.checked ? "block" : "none";
      if (!this.checked) {
        waiverTypeSection
          .querySelectorAll('input[type="radio"]')
          .forEach((r) => (r.checked = false));
      }
      toggleCommoditySections();
    });
  }

  auditTypeSelect.addEventListener("change", toggleCommoditySections);

  toggleCommoditySections(); // ✅ Call only AFTER everything is declared

  // Commodity checkbox toggle
  document.querySelectorAll("[data-commodity-toggle]").forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      const type = checkbox.dataset.type;
      const groupCode = checkbox.value;
      const target = document.getElementById(`${type}__${groupCode}Fields`);
      if (target) target.style.display = checkbox.checked ? "block" : "none";
    });
  });

  // Form submission logic
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    errorBox.style.display = "none";
    successBox.style.display = "none";

    const auditType = auditTypeSelect.value;
    const formData = new FormData(form);
    const checkedCommodities = [
      ...document.querySelectorAll(
        `[data-commodity-toggle][data-type="${auditType}"]:checked`
      ),
    ];

    if (!waiverCheckbox.checked && checkedCommodities.length === 0) {
      return showError("Select at least one commodity.");
    }

    if (!waiverCheckbox.checked) {
      for (const checkbox of checkedCommodities) {
        const group = checkbox.value;
        const weight = formData.get(`${auditType}_total_weight_${group}`);
        const picture = formData.get(`${auditType}_audit_picture_${group}`);

        if (!weight) return showError(`Total weight for ${group} is required.`);
        if (!picture || !picture.name)
          return showError(`Picture for ${group} is required.`);
      }
    }

    if (auditType === "verification" && !waiverCheckbox.checked) {
      const compliance = document.querySelector(
        "input[name='compliance']:checked"
      );
      if (!compliance) return showError("Compliance selection is required.");
    }

    fetch(form.getAttribute("action") || "/audits/submit/audit/", {
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
          Swal.fire({
            icon: "success",
            title: "Success!",
            text: "Audit saved successfully.",
            confirmButtonText: "OK",
          }).then(() => {
            window.location.href = "/audits/dashboard/";
          });
        } else {
          showError(data.message || "Something went wrong.");
        }
      })
      .catch(() => {
        showError("Unexpected server error.");
      });

    function showError(msg) {
      errorBox.innerText = msg;
      errorBox.style.display = "block";
    }
  });
});
