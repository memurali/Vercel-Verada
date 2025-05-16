document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("audit-schedule-form");
    const errorBox = document.getElementById("error-box");

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const formData = new FormData(form);

        fetch("/audits/audit/schedule/submit/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: 'success',
                    title: 'Success!',
                    text: 'Audit scheduled successfully.',
                    confirmButtonText: 'OK',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    allowEnterKey: true
                }).then((result) => {
                    if (result.isConfirmed) {
                        window.location.href = '/audits/dashboard/';
                    }
                });
            } else {
                errorBox.innerText = data.message;
                errorBox.style.display = "block";
            }
        })
        .catch(() => {
            errorBox.innerText = "Server error.";
            errorBox.style.display = "block";
        });
    });
});

$(document).ready(function() {
    function fetchAddressesByLocations(locationIds) {
        $.ajax({
            url: '/audits/get-addresses/',
            type: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            data: JSON.stringify({ locations: locationIds }),
            contentType: 'application/json',
            success: function(response) {
                const addressSelect = $('#audit-address-dropdown');
                addressSelect.empty();
                addressSelect.append('<option value="">Select Address</option>');
                response.addresses.forEach(function(addr) {
                    addressSelect.append('<option value="' + addr.id + '">' + addr.full_address + '</option>');
                });
            },
            error: function(xhr) {
                console.error('Error fetching addresses:', xhr.responseText);
            }
        });
    }

    // Attach event inside dropdown open event
    $(document).on('change', '.audit-location-checks', function() {
        const selectedLocations = $(this).val();  // array of selected values
        if (selectedLocations && selectedLocations.length > 0) {
            fetchAddressesByLocations(selectedLocations);
        } else {
            $('#audit-address-dropdown').empty().append('<option value="">Select Address</option>');
        }
    });

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    $('.select2').select2({
        width: '100%',
        placeholder: 'Select an option',
        allowClear: true
      });      
});

