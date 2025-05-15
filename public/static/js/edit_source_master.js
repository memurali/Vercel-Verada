
// Source Master 

document.getElementById("source_master-form").addEventListener("submit", function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const successBox = document.getElementById("success-box");
    const errorBox = document.getElementById("error-box");

    fetch("/waste/source/updates/", {
        method: "POST",
        headers: {
            "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: formData,
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            successBox.innerText = data.message;
            successBox.style.display = "block";
            errorBox.style.display = "none";
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: data.message,
                confirmButtonText: 'OK',
                allowOutsideClick: false,     // Prevent click outside
                allowEscapeKey: false,        // Prevent ESC key
                allowEnterKey: true           // Optional: allow Enter to confirm
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.href = '/waste/source/dashboard/';
                }
            });
        } else {
            errorBox.innerText = data.message;
            errorBox.style.display = "block";
            successBox.style.display = "none";
        }
    })
    .catch(() => {
        errorBox.innerText = "Unexpected error occurred.";
        errorBox.style.display = "block";
    });
});


// Delete 
document.getElementById("delete_btn").addEventListener("click", function (e) {
    e.preventDefault();

    const selectedIds = [];
    const checkboxes = document.querySelectorAll(".checkbox:checked");

    checkboxes.forEach((checkbox) => {
        selectedIds.push(checkbox.value);
    });

    if (selectedIds.length === 0) {
        alert("No rows selected to delete.");
        return;
    }

    // Show a confirmation message
    const confirmation = confirm("Are you sure you want to delete the selected waste groups?");
    if (confirmation) {
        // Send a request to delete the selected rows
        fetch('/waste/source/delete/', {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                waste_source_master_ids: selectedIds
            })
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.success) {
                // Remove the deleted rows from the table
                checkboxes.forEach((checkbox) => {
                    if (checkbox.checked) {
                        checkbox.closest("tr").remove();
                    }
                });
                document.getElementById("feedback-box").innerText = "Selected rows deleted successfully.";
                document.getElementById("feedback-box").style.display = "block";
            } else {
                alert("Failed to delete selected rows.");
            }
        })
        .catch((err) => {
            alert("Error: " + err);
        });
    }
});
