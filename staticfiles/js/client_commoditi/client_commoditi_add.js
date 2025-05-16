$("#moveright").click(function () {
    $("#country > option:selected").each(function () {
        $(this).remove().appendTo("#planets");
    });
});

$("#moveleft").click(function () {
    $("#planets > option:selected").each(function () {
        $(this).remove().appendTo("#country");
    });
});

document.addEventListener("DOMContentLoaded", function() {
    const moveRight = document.getElementById("moveright");
    const moveLeft = document.getElementById("moveleft");
    const available = document.getElementById("country");
    const selected = document.getElementById("planets");
    const submitBtn = document.getElementById("submit-commodities");

    moveRight.addEventListener("click", function() {
        moveSelected(available, selected);
    });

    moveLeft.addEventListener("click", function() {
        moveSelected(selected, available);
    });

    function moveSelected(from, to) {
        const selectedOptions = Array.from(from.selectedOptions);
        selectedOptions.forEach(option => {
            from.removeChild(option);
            to.appendChild(option);
        });
    }

    submitBtn.addEventListener("click", function() {
        const selectedCommodities = Array.from(selected.options)
            .filter(opt => !opt.disabled)
            .map(opt => opt.value);

        if (selectedCommodities.length === 0) {
            Swal.fire({
                icon: "warning",
                title: "No Commodities Selected",
                text: "Please select at least one commodity before submitting.",
            });
            return;
        }

        fetch("/client/commodities/mapping/submit/", {
            method: "POST",
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ commodity_ids: selectedCommodities }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                Swal.fire({
                    icon: "success",
                    title: "Success!",
                    text: "Commodities mapped successfully!",
                    confirmButtonText: "OK"
                }).then(() => {
                    window.location.href = "/client/commodities/dashboard/";
                });
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Error",
                    text: data.message || "Something went wrong.",
                });
            }
        })
        .catch(() => {
            Swal.fire({
                icon: "error",
                title: "Server Error",
                text: "Unexpected server error occurred.",
            });
        });
    });
});
