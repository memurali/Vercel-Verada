function editUser(element) {
  let row = element.closest("tr");
  let userId = row.getAttribute("data-user-id");

  if (!userId) {
    alert("User ID not found for editing.");
    return;
  }

  window.location.href = `/user/edit/${userId}/`;
}
document.addEventListener("DOMContentLoaded", function () {
  const input = document.getElementById("user-search-input");
  const form = document.getElementById("user-search-form");

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

filterTable("user-search-input", "usermanagement-table");
