$(document).ready(function () {
    const $newSection = $('#master_new');
    const $existSection = $('#master_exist');

    // Function to enable/disable all inputs inside a section
    function toggleInputs($section, enabled) {
        $section.find('input, select, textarea').each(function () {
            $(this).prop('disabled', !enabled);
        });
    }

    // Initial hide and disable all
    $newSection.hide();
    $existSection.hide();
    toggleInputs($newSection, false);
    toggleInputs($existSection, false);

    $("input[name='source_master_cat']").change(function () {
        const selectedValue = $(this).val();

        if (selectedValue === "yes") {
            $newSection.show();
            toggleInputs($newSection, true);
            $existSection.hide();
            toggleInputs($existSection, false);
        } else if (selectedValue === "no") {
            $existSection.show();
            toggleInputs($existSection, true);
            $newSection.hide();
            toggleInputs($newSection, false);
        }
    });

    // Trigger once on page load to set correct visibility and enable state
    $("input[name='source_master_cat']:checked").trigger("change");
});


document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    
    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const sourceType = document.querySelector("input[name='source_master_cat']:checked");

        if (!sourceType) {
            return Swal.fire("Error", "Please select source type (New or Existing)", "error");
        }

        formData.append("source_type", sourceType.value);

        fetch("/waste/source/store/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
            body: formData,
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Success!",
                    text: "Data submitted successfully.",
                }).then(() => {
                    window.location.href = "/waste/source/dashboard/";
                });
            } else {
                Swal.fire("Error", data.message || "Something went wrong.", "error");
            }
        })
        .catch(() => {
            Swal.fire("Error", "Unexpected server error.", "error");
        });
    });
});
