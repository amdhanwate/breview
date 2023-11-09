function addNewReview(e, id) {
    e.preventDefault();

    const elements = e.target.elements

    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify({
        "username": localStorage.getItem("username"),
        "review": elements[1].value,
        "rating": elements[0].value
    });

    var requestOptions = {
        method: 'POST',
        headers: myHeaders,
        body: raw,
        redirect: 'follow'
    };

    fetch(`/api/v1/breweries/${id}/review`, requestOptions)
        .then(response => response.json())
        .then(result => {
            if (result.status === "ok") {
                window.location.reload();
                return;
            }

            return alert(result.message)
        })
        .catch(error => alert("Somethin went wrong!"));
}