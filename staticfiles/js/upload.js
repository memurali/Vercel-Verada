document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const errorDiv = document.getElementById("login-error");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        fetch("/upload_api/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                body: formData,
            })
            .then((res) => res.json())
            .then((data) => {

                console.log(data,">>>>>>>>>")

            })
    })


});
