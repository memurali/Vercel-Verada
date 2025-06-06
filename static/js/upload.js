document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const errorDiv = document.getElementById("login-error");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const formData = new FormData(form);
        const csrfToken = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        ).value;

        fetch('/api/upload_api')
            .then(async res => {
                const contentType = res.headers.get("content-type");
                const text = await res.text();
                if (!res.ok) throw new Error(`Server error: ${res.status}`);
                if (!contentType.includes("application/json")) {
                    console.error("Not JSON:", text);
                    throw new Error("Expected JSON, got something else.");
                }
                return JSON.parse(text);
            })
            .then(data => console.log(data))
            .catch(err => console.error(err));

    })


});
