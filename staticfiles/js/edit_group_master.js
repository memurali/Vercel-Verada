// document.getElementById("waste-group-form").addEventListener("submit", function (e) {
//     e.preventDefault();

//     const form = e.target;
//     const formData = new FormData(form);
//     const successBox = document.getElementById("success-box");
//     const errorBox = document.getElementById("error-box");

//     fetch("/waste/update/", {
//         method: "POST",
//         headers: {
//             "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
//         },
//         body: formData,
//     })
//     .then(res => res.json())
//     .then(data => {
//         if (data.success) {
//             successBox.innerText = data.message;
//             successBox.style.display = "block";
//             errorBox.style.display = "none";
//             Swal.fire({
//                 icon: 'success',
//                 title: 'Success!',
//                 text: data.message,
//                 confirmButtonText: 'OK',
//                 allowOutsideClick: false,     // Prevent click outside
//                 allowEscapeKey: false,        // Prevent ESC key
//                 allowEnterKey: true           // Optional: allow Enter to confirm
//             }).then((result) => {
//                 if (result.isConfirmed) {
//                     window.location.href = '/waste/group/dashboard/';
//                 }
//             });
//         } else {
//             errorBox.innerText = data.message;
//             errorBox.style.display = "block";
//             successBox.style.display = "none";
//         }
//     })
//     .catch(() => {
//         errorBox.innerText = "Unexpected error occurred.";
//         errorBox.style.display = "block";
//     });
// });

function getCSRFToken() {
    let name = 'csrftoken';
    let cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        let c = cookie.trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return '';
}



document.getElementById("delete_btn").addEventListener("click", function (e) {
    e.preventDefault();

    const selectedIds = [];
    const checkboxes = document.querySelectorAll(".checkbox:checked");

    checkboxes.forEach((checkbox) => {
        selectedIds.push(checkbox.value);
    });

    if (selectedIds.length === 0) {
        Swal.fire({
            title: 'No selection',
            text: 'Please select at least one waste group to delete.',
            icon: 'warning',
            confirmButtonText: 'OK'
        });
        return;
    }

    // Show a confirmation message
    Swal.fire({
        title: 'Are you sure?',
        text: "You won't be able to revert this!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!'
    }).then((result) => {
        if (result.isConfirmed) {
            // CSRF token handling
            // const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            // if (!csrfToken) {
            //     console.error("CSRF token element not found!");
            //     return;
            // }

            // Send the delete request
            fetch('/waste/delete/', {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken(), // function below
                    },
                    body: JSON.stringify({
                        waste_group_master_ids: selectedIds
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

                        Swal.fire({
                            title: "Deleted!",
                            text: "The selected waste groups have been deleted.",
                            icon: "success",
                            confirmButtonText: 'OK'
                        });
                    } else {
                        Swal.fire({
                            title: "Error",
                            text: "Failed to delete selected waste groups.",
                            icon: "error",
                            confirmButtonText: 'OK'
                        });
                    }
                })
                .catch((err) => {
                    console.error("Error: ", err);
                    Swal.fire({
                        title: "Error",
                        text: "An unexpected error occurred while deleting.",
                        icon: "error",
                        confirmButtonText: 'OK'
                    });
                });
        }
    });
});