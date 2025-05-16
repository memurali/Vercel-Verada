document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("commodity-doc-form");
  const successBox = document.getElementById("doc-success");
  const errorBox = document.getElementById("doc-error");
  const downloadLink = document.getElementById("download-link");

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const fileInput = document.getElementById("supporting_document");
    const file = fileInput.files[0];

    if (!file) {
      errorBox.textContent = "Please select a file.";
      errorBox.style.display = "block";
      successBox.style.display = "none";
      return;
    }

    const formData = new FormData(form);
    const csrfToken = document.querySelector(
      "[name=csrfmiddlewaretoken]"
    ).value;

    fetch("{% url 'core:upload_doc_commoditi' %}", {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          successBox.style.display = "block";
          errorBox.style.display = "none";
          downloadLink.href = data.file_url;
          downloadLink.style.display = "inline-block";
          downloadLink.innerText = "Download " + data.file_name;
        } else {
          errorBox.textContent = data.message || "Upload failed.";
          errorBox.style.display = "block";
          successBox.style.display = "none";
        }
      })
      .catch(() => {
        errorBox.textContent = "Unexpected error.";
        errorBox.style.display = "block";
      });
  });

  const input = document.getElementById("commodity-search-input");

  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") {
      e.preventDefault();
      form.submit();
    }
  });
});
