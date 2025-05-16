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

filterTable("scheduled-audit-search", "scheduled-audits");
filterTable("verification-audit-search", "verification-audits");
filterTable("inital-audit-search", "inital-audits");