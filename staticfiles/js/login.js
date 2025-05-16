document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("login-form");
    const errorDiv = document.getElementById("login-error");

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("login-email").value;
        const password = document.getElementById("login-password").value;

        fetch("/api/auth/ajax-login/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            body: JSON.stringify({ email, password })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.mfa) {
                sessionStorage.setItem("mfa_session_token", data.session_token);
                window.location.href = data.redirect_url;
            } else {
                errorDiv.textContent = data.message || "Login failed";
            }
        })
        .catch(error => {
            errorDiv.textContent = "An error occurred. Please try again.";
            console.error("Login error:", error);
        });
    });

    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
});
