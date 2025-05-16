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

filterTable("waste-source-master-search", "waste-source-master-table");
