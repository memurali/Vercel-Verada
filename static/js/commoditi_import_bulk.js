var fieldLinks;
var inputOri;

$('#upload_file').on('change', function (e) {
    e.preventDefault();

    var file = this.files[0];

    if (!file) {
        alert("Please select a file.");
        return;
    }

    var formData = new FormData();
    formData.append('file', file);

    $.ajax({
        url: '/commodities/upload_excel/', // your Django upload endpoint
        type: 'POST',
        data: formData,
        processData: false, // prevent jQuery from processing data
        contentType: false, // prevent jQuery from setting content type
        success: function (res) {
            inputOri = res
            // console.log("Request: " + inputOri);
            fieldLinks = $("#original").fieldsLinker("init", inputOri);
            // $(".fieldLinkerSave").on("click", function () {
            //     var results = fieldLinks.fieldsLinker("getLinks");
            //     $("#output").html("output => " + JSON.stringify(results));
            // });

            $(".fieldLinkerSave").on("click", function () {
                var results = fieldLinks.fieldsLinker("getLinks");
                $("#output").html("output => " + JSON.stringify(results));
            
                // Convert the list of links into a mapping object: { "Excel Column": "Model Field" }
                var mappings = {};
                results['links'].forEach(function (link) {
                    mappings[link.from] = link.to;
                });
            
                // Make sure the backend gave us the full original Excel data
                var excelData = inputOri.Lists; // assuming backend includes full row data here
            
                if (!excelData || excelData.length === 0) {
                    alert("No data rows found.");
                    return;
                }
            
                var payload = {
                    mappings: mappings,
                    data: inputOri.data  
                };
            
                // Save mapped data
                $.ajax({
                    url: '/commodities/save_mapped_data/',  // Your new API to insert into the DB
                    type: 'POST',
                    contentType: 'application/json',
                    headers: {
                        "X-CSRFToken": getCSRFToken()
                    },
                    data: JSON.stringify(payload),
                    success: function (response) {
                        if (response.status == "success"){
                            $('#upload-errors').hide().empty(); // hide any previous errors

                            Swal.fire({
                                icon: 'success',
                                title: 'Success!',
                                text: `Data saved successfully inserted.`,
                                confirmButtonText: 'OK',
                                allowOutsideClick: false,     // Prevent click outside
                                allowEscapeKey: false,        // Prevent ESC key
                                allowEnterKey: true           // Optional: allow Enter to confirm
                            }).then((result) => {
                                if (result.isConfirmed) {
                                    window.location.href = '/commodities/dashboard/';
                                }
                            });
                        }
                        else{
                            alert("No Unique Data available: ")
                        }
                    },
                    error: function (xhr) {
                        const errorBox = $('#upload-errors');
                        errorBox.empty();
                        
                        if (xhr.status === 422) {
                            const response = JSON.parse(xhr.responseText);
                            if (response.errors && Array.isArray(response.errors)) {
                                errorBox.show();
                                response.errors.forEach(err => {
                                    errorBox.append(`<div>• ${err}</div>`);
                                });
                            }
                        } else {
                            Swal.fire({
                                icon: 'error',
                                title: 'Unexpected Error',
                                text: xhr.responseJSON?.message || 'Something went wrong!',
                            });
                        }
                    }
                });
            });

        },
        error: function (inputOri, error) {
            alert('Data: ' + inputOri);
            console.log("Request: " + inputOri);
        }

    });
});

function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

document.getElementById('upload_file').addEventListener('change', function(e) {
    const fileName = e.target.files.length > 0 ? e.target.files[0].name : 'No file chosen';
    document.querySelector('.file-name').textContent = fileName;
});