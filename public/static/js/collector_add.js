document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("collector-form");
    const successBox = document.getElementById("collector-success");
    const errorBox = document.getElementById("collector-error");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch("/collectors/create/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: formData
            })
            .then((res) => res.json())
            .then((data) => {
                if (data.success) {
                    successBox.style.display = "block";
                    errorBox.style.display = "none";
                    form.reset();
                    Swal.fire({
                        icon: 'success',
                        title: 'Success!',
                        text: 'Waste collector added successfully.',
                        confirmButtonText: 'OK',
                        allowOutsideClick: false, // Prevent click outside
                        allowEscapeKey: false, // Prevent ESC key
                        allowEnterKey: true // Optional: allow Enter to confirm
                    }).then((result) => {
                        if (result.isConfirmed) {
                            window.location.href = '/collectors/dashboard/';
                        }
                    });
                } else {
                    errorBox.innerText = data.message;
                    errorBox.style.display = "block";
                }
            })
            .catch(() => {
                errorBox.innerText = "Unexpected error occurred.";
                errorBox.style.display = "block";
            });
    });
});



// Download template 

async function download_template(url, collector_type) {
    try {
        // Fetch the file from the server
        const response = await fetch(url);

        // Check if the response is ok (status 200)
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        // Convert the response into a blob (binary data)
        const blob = await response.blob();

        // Format the filename with the generator and location values
        const filename = `template_${collector_type}.xlsx`.replace(/\s+/g, '_');

        // Create a link element to trigger the download
        const link = document.createElement('a');
        link.href = window.URL.createObjectURL(blob);
        link.download = filename;

        // Append the link to the document body, trigger the click, then remove the link
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    } catch (err) {
        // Handle any errors that occur during the fetch or download process
        console.error("Download failed:", err);
        alert("An error occurred while downloading the file.");
    }
}

document.querySelector('.download_template').addEventListener('click', async function (e) {
    e.preventDefault();


    $(document).ready(function () {
        const collector_type = document.getElementById('collector_type').value;

        const url =
            `/collectors/download-template/?collector_type=${encodeURIComponent(collector_type)}`;

        download_template(url, collector_type)

    })

});