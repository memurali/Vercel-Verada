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
        url: '/generators/upload_excel', // your Django upload endpoint
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
                $("#spinner").css({
                    'display': 'block'
                })
                // $('.import-btn').prop('disabled', true);
                var results = fieldLinks.fieldsLinker("getLinks");
                // $("#output").html("output => " + JSON.stringify(results));
            
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
                    url: '/generators/save_mapped_data',  // Your new API to insert into the DB
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify(payload),
                    success: function (response) {
                        if (response['status'] == 'success'){
                            alert("Data saved successfully");
                            $("#spinner").css({
                                'display': 'none'
                            })
                            $('.import-btn').prop('disabled', false);
                        }
                        else{
                            alert("No Unique Data available")
                            $("#spinner").css({
                                'display': 'none'
                            })
                            $('.import-btn').prop('disabled', false);
                        }
                    },
                    error: function (xhr) {
                        alert("Error saving data: " + xhr.responseText);
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


