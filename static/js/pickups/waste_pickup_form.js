// static/js/waste_pickup_form.js
document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);

    fetch("/generators/pickup/submit/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
            .value,
        },
        body: formData,
      })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          Swal.fire("Success", "Waste pickup submitted!", "success").then(
            () => {
              window.location.href = "/generators/pickup/dashboard/";
            }
          );
        } else {
          Swal.fire("Error", data.message || "Something went wrong", "error");
        }
      })
      .catch(() => {
        Swal.fire("Error", "Unexpected error occurred", "error");
      });
  });
});

// $(document).ready(function () {
//   function fetchPickUpFoodType(group_id) {
//     $.ajax({
//       url: `/generators/get/food_type/${group_id}/`,
//       type: "GET",
//       headers: {
//         "X-CSRFToken": getCSRFToken(),
//       },
//       contentType: "application/json",
//       success: function (response) {
//         const foodTypeSelect = $("#food_type");
//         foodTypeSelect.empty();
//         foodTypeSelect.append('<option value="">Select Food Type</option>');
//         response.commodities.forEach(function (commoditi) {
//           foodTypeSelect.append(
//             '<option value="' + commoditi.id + '">' + commoditi.name + "</option>"
//           );
//         });
//       },
//       error: function (xhr) {
//         console.error("Error fetching food type:", xhr.responseText);
//       },
//     });
//   }

//   // Attach event inside dropdown open event
//   $(document).on("change", "#waste_type", function () {
//     const selectedGroup = $(this).val(); // array of selected values
//     if (selectedGroup && selectedGroup.length > 0) {
//       fetchPickUpFoodType(selectedGroup);
//     } else {
//       $("#food_type")
//         .empty()
//         .append('<option value="">Select Food Type</option>');
//     }
//   });

//   function getCSRFToken() {
//     return document.querySelector("[name=csrfmiddlewaretoken]").value;
//   }
// });

$(document).ready(function () {

  function fetchAddressesByLocations(locationIds) {
    $.ajax({
      url: '/audits/get-addresses/',
      type: 'POST',
      headers: {
        'X-CSRFToken': getCSRFToken()
      },
      data: JSON.stringify({
        locations: locationIds
      }),
      contentType: 'application/json',
      success: function (response) {
        const addressSelect = $('#address');
        addressSelect.empty();
        addressSelect.append('<option value="">Select Address</option>');
        response.addresses.forEach(function (addr) {
          addressSelect.append('<option value="' + addr.id + '">' + addr.full_address + '</option>');
        });
      },
      error: function (xhr) {
        console.error('Error fetching addresses:', xhr.responseText);
      }
    });
  }

  // Attach event inside dropdown open event
  $(document).on('change', '#generator', function () {
    const selectedLocations = $(this).val(); // array of selected values
    if (selectedLocations && selectedLocations.length > 0) {
      fetchAddressesByLocations(selectedLocations);
    } else {
      $('#address').empty().append('<option value="">Select Address</option>');
    }
  });


});

function getCSRFToken() {
  return document.querySelector('[name=csrfmiddlewaretoken]').value;
}



// Download template 

async function download_template(url, generator, location) {
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
    const filename = `template_${generator}_${location}.xlsx`.replace(/\s+/g, '_');
    
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
    const generator_id = document.getElementById('generator').value;
    const location_id = document.getElementById('address').value;

    var form_data = {
      'gen_id': generator_id,
      'location_id': location_id
    }

    $.ajax({
      url: '/generators/download_temp_getting_names',
      type: 'POST',
      data: form_data,
      headers: {
        'X-CSRFToken': getCSRFToken()
      },
      success: function (res) {

        console.log(res[0], "..............")
        var generator = res[0]['name']
        var location = res[0]['full_address']

        const url =
          `/generators/download-template/?generator=${encodeURIComponent(generator)}&location=${encodeURIComponent(location)}`;

          download_template(url, generator, location)

      }
    })
  })

});