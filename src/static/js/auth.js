
const signup_container = document.getElementById("signup_container");
const login_container = document.getElementById("login_container");

const login_form = document.forms.namedItem("login_form")
const signup_form = document.forms.namedItem("signup_form")

document.querySelector(".create-an-account-text").addEventListener("click", () => {
    signup_container.style.display = "block";
    login_container.style.display = "none";
})

document.querySelector(".login-to-your-account-text").addEventListener("click", () => {
    signup_container.style.display = "none";
    login_container.style.display = "block";
})

login_form.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();

    login_form.classList.add("was-validated");

    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({
        "username": login_form.elements.namedItem("username").value,
        "password": login_form.elements.namedItem("password").value
    });

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    fetch("/api/v1/login", requestOptions)
        .then(response => response.json())
        .then(result => {
            if (result["status"] === 'ok') {
                localStorage.setItem("access_token", result["access_token"])
                localStorage.setItem("refresh_token", result["refresh_token"])
                localStorage.setItem("username", result["username"])
                window.location.href = "/";
            } else {
                alert(result["error"])
            }
        })
        .catch(error => {
            alert(result["error"])
        });
})

signup_form.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopPropagation();

    signup_form.classList.add("was-validated");

    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({
        "username": signup_form.elements.namedItem("username").value,
        "password": signup_form.elements.namedItem("password").value,
        "password_confirmation": signup_form.elements.namedItem("confirm_password").value,
        "full_name": signup_form.elements.namedItem("full_name").value,
    });

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    fetch("/api/v1/signup", requestOptions)
        .then(response => response.json())
        .then(result => {
            if (result["status"] === 'ok') {
                localStorage.setItem("access_token", result["access_token"])
                localStorage.setItem("refresh_token", result["refresh_token"])
                localStorage.setItem("username", result["username"])
                window.location.href = "/";
            } else {
                console.log(result);
                alert(result["error"])
            }
        })
        .catch(error => alert(error));
})

