let date;
let distance;
let category;
let search_type;

document.addEventListener('DOMContentLoaded', function() {
    date = document.querySelector('#dateDropdown');
    distance = document.querySelector('#distanceDropdown');
    category = document.querySelector('#categoryDropdown');
    search_type = document.querySelector('.search-type');

    
    search_type.addEventListener('change', filterResults);
    document.querySelectorAll('.dropdown').forEach((select) => select.addEventListener('change', filterResults));
});

function filterResults() {
    
    const selectedDistance = distance.value
    const selectedDate = date.value
    const selectedCategory = category.value
    const selectedSearch_type = search_type.checked ? 'Group' : 'Event';
    const title = document.querySelector('.title');
    const userTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

    if (search_type.checked) {
        date.parentNode.style.visibility = 'hidden'; // Make the element not visible
    } else {
        date.parentNode.style.visibility = 'visible'; // Make the element visible
    }

    console.log('search type: ', selectedSearch_type);
    
        
    fetch(`/search/filter/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({
            'date': selectedDate,
            'userTimezone': userTimezone,
            'distance': selectedDistance,
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
        // Update the eventList element with the filtered data
        const eventListElement = document.getElementById('eventList');
        eventListElement.innerHTML = data.html; // Assuming the server sends back HTML content in the 'html' field of the response JSON
        title.innerHTML = `There are ${data.count} ${selectedSearch_type}(s) !`;
    })
    .catch(error => {
        console.error(error);
    });


    // console.log('distance', selectedDistance);
    // console.log('category', selectedCategory);

    

}