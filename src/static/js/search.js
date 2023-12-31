document.querySelector(".username").innerHTML = localStorage.getItem("username");

const brewery_container = document.querySelector(".brewery_container");
const brewery_search_loader = document.querySelector(".brewery_search_loader");
const noBreweriesFound = document.querySelector(".no-breweries-found");
const lonelyContainer = document.querySelector(".lonely-container")
const searchFormSubmitBtn = document.querySelector(".searchFormSubmitBtn");

function populate_brewery_card(info) {
    if (info["phone"] == null) info["phone"] = "Not Available";
    html = `
    <div class="card-body d-flex justify-content-between align-items-center bg-light rounded-3">
        <div class="d-flex justify-content-center">
            <div class="" style="min-width: 400px;">
                <p class="card-title h5 mb-1 fw-semibold">${info["name"]}</p>
                <p class="mb-0 d-flex align-items-center ${info["rating"] == null ? 'd-none' : ''}">
                    <span class="fw-bold me-2">${info["rating"]}</span>
                    <i class="bg-dange me-0 p-1 rounded text-warning bx bxs-star"></i>
                    <i class="bg-dange me-0 p-1 rounded text-warning bx bxs-star"></i>
                    <i class="bg-dange me-0 p-1 rounded text-warning bx bxs-star"></i>
                    <i class="bg-dange me-0 p-1 rounded text-warning bx bxs-star"></i>
                    <i class="bg-dange me-0 p-1 rounded text-warning bx bxs-star-half"></i>
                    <span class="ms-2 text-muted">(${info["review_count"]} reviews)</span>
                </p>
                <p class="mb-0 d-flex align-items-center ${info["rating"] == null ? '' : 'd-none'}">
                    Not rated yet
                </p>
            </div>
            <div>
                <p class="card-text mb-2 text-muted fw-semibold">${info["address"]}, ${info["city"]}, ${info["state"]}</p>
                <p class="card-text text-success fw-semibold">
                    <span class="me-3">
                        <i class="bx bx-phone-call"></i>
                        ${info["phone"]}
                    </span>
                    <a href="${info["website"]}" class="card-text text-orange text-decoration-none">
                        <i class="bx bx-globe"></i>
                        Visit site
                    </a>
                </p>
            </div>
        </div>
        <div class="text-center">
            <a href="/brewery/${info["id"]}" class="btn btn-primary">See
                Details</a>
        </div>
    </div>
    `

    return html;
}

const getBreweries = (by, value) => {
    var requestOptions = {
        method: 'GET',
        redirect: 'follow'
    };

    searchFormSubmitBtn.classList.add("disabled");
    lonelyContainer.classList.add("d-none")
    noBreweriesFound.classList.add("d-none");
    brewery_search_loader.classList.remove("d-none");

    const date1 = new Date();
    const url = encodeURI(`/api/v1/breweries?by_${by}=${value}&per_page=5`);
    console.log(url);
    fetch(url, requestOptions)
        .then(response => response.json())
        .then(result => {
            const date2 = new Date();
            brewery_search_loader.classList.add("d-none");

            if (Array.isArray(result.data) && result.data.length == 0) {
                noBreweriesFound.classList.remove("d-none");
                return;
            }

            const duration = ((date2 - date1) / (60 * 60)).toFixed(2);
            brewery_container.innerHTML = '<p class="small text-black-50 mb-2 results-info"></p>';
            document.querySelector(".results-info").innerHTML = `fetched ${result.data.length} results in ${duration}s`
            Array.from(result.data).forEach(brewery => {
                console.log(brewery);
                const brewery_card = document.createElement("div");
                brewery_card.classList.add("card", "mb-3");
                brewery_card.innerHTML = populate_brewery_card(brewery);
                brewery_container.appendChild(brewery_card);
            })
        })
        .catch(error => console.log('error', error))
        .finally(() => searchFormSubmitBtn.classList.remove("disabled"))
}

function searchBreweries(event) {
    event.preventDefault();
    event.stopPropagation();

    const filter_by = document.getElementById("filter_by")
    const filter_value = filter_by.value;

    const search_bar = document.getElementById("search_bar");
    const search_bar_value = search_bar.value;

    getBreweries(filter_value, search_bar_value);
}

const populate_suggestion_in_form = () => {
    const brewery_search_form = document.forms.namedItem("brewery_search_form")

    brewery_search_form.elements.namedItem("filter_by").value = "name";
    brewery_search_form.elements.namedItem("search_bar").value = "32 North Brewing Co";
}
