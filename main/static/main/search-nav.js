let date;
let distance;
let category;
let search_type;
let search_bar;

document.addEventListener('DOMContentLoaded', function() {
    date = document.querySelector('#dateDropdown');
    distance = document.querySelector('#distanceDropdown');
    category = document.querySelector('#categoryDropdown');
    search_type = document.querySelector('.search-type');
    search_bar = document.querySelector('.search-box-input');
    search_button = document.querySelector('.search-box-button');

    search_bar.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            filterResults();
        }
    });

    search_button.addEventListener('click', filterResults);
    search_type.addEventListener('change', filterResults);
    document.querySelectorAll('.dropdown').forEach((select) => select.addEventListener('change', filterResults));
});


function filterResults() {
    const query = search_bar.value;
    const selectedDate = date.value
    const selectedDistance = distance.value
    const lat = document.getElementById('location-lat').value;
    const lng = document.getElementById('location-lng').value;
    const selectedCategory = category.value
    const selectedSearch_type = search_type.checked ? 'Group' : 'Event';
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    if (search_type.checked) {
        date.style.visibility = 'hidden'; // Make the element not visible
    } else {
        date.style.visibility = 'visible'; // Make the element visible
    }    
        
    fetch(`/search/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({
            'query': query,
            'date': selectedDate,
            'userTimezone': userTimezone,
            'distance': selectedDistance,
            'lat': lat,
            'lng': lng,
            'category': selectedCategory,
            'search_type': selectedSearch_type,
        })
    })
    .then(response => {
        if (response.status === 200) {
            return response.json();
        } else {
            console.log(response);
        }
    })
    .then(data => {
        const eventListElement = document.getElementById('eventList');
        eventListElement.innerHTML = data.html;
        const title = document.querySelector('.title');
        title.innerHTML = `There are ${data.count} ${selectedSearch_type}(s) !`;
    })
    .catch(error => {
        console.error(error);
    });
}