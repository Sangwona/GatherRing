document.addEventListener('DOMContentLoaded', function() {
    const event_id = document.querySelector('#button-div').getAttribute('data-event-id');
    const user_is_authenticated = document.querySelector('#button-div').getAttribute('data-is-authenticated');

    const join_btn = document.querySelector('.join_button');
    const request_btn = document.querySelector('.request_button');
    const cancel_btn = document.querySelector('.cancel-event-btn');
    const delete_btn = document.querySelector('.delete-btn');
    const upload_btn = document.querySelector('.photo_upload_button');
    const upload_cancel_btn = document.querySelector('#cancel_form');
    const view_member_btn = document.querySelector('.view-members-btn');
    if (join_btn) {
        join_btn.addEventListener('click', () => joinOrLeaveEvent(event_id, user_is_authenticated));
    }
    if (request_btn) {
        request_btn.addEventListener('click', () => createOrDeleteEventRequest(event_id, user_is_authenticated));
    }
    if (cancel_btn) {
        cancel_btn.addEventListener('click', (e) => cancelOrActiveEvent(e, event_id));
    }
    if (delete_btn) {
        delete_btn.addEventListener('click', () => deleteEvent(event_id));
    }

    upload_btn.addEventListener('click', () => showPhotoForm(event_id));
    upload_cancel_btn.addEventListener('click', cancelPhotoForm);
    view_member_btn.addEventListener('click', () => showEventAttendees(event_id));

    initMap();
    load_photos(event_id);
});

function joinOrLeaveEvent(event_id, user_is_authenticated) {
    if (user_is_authenticated != "True") { 
        alert("You must be logged in to join the event.");
    }
    else {
        fetch(`/event/toggle_attendance/${event_id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.joined) {
                join_btn.textContent = "Leave Event";
            }
            else {
                join_btn.textContent = "Join Event";
            }
            document.querySelector(`.attendee_count`).textContent = `${data.attendee_count}`;        
        })
    }
}

function createOrDeleteEventRequest(event_id, user_is_authenticated) {
    if (user_is_authenticated != "True") { 
        alert("You must be logged in to join the event.");
    }
    else {
        fetch(`/event/toggle_request/${event_id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.requested) {
                    request_btn.textContent = "Withdraw Request";
                }
                else {
                    request_btn.textContent = "Request to Join";
                }
            })
    }
}

function cancelOrActiveEvent(e, event_id) {
    const isReactive = e.currentTarget.classList.contains('reactive');
    
    fetch(`/event/change_status/${event_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
        body: JSON.stringify({
            'action': isReactive ? 'reactive' : 'cancel',
        })
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.isActive) { 
                cancel_btn.classList.remove('reactive')
                cancel_btn.classList.add('cancel')
                cancel_btn.textContent = 'Cancel Event'
            } else {
                cancel_btn.classList.remove('cancel')
                cancel_btn.classList.add('reactive')
                cancel_btn.textContent = 'Reactivate Event'
            }
        })
        .catch((error) => console.log(error))
}

function showEventAttendees(event_id) {
    fetch(`/event/attendees/${event_id}/`)
        .then(res => res.json())
        .then(members => {
            const membersList = document.querySelector('#members-list');
            membersList.innerHTML = '';
            members.forEach(member => {
                const li = document.createElement('li');
                li.innerHTML = `<a href="/user/profile/${member.id}/">${member.username}</a>`;
                membersList.appendChild(li);
            });

            document.querySelector('#popup-overlay').style.display = 'block';
            document.querySelector('#members-popup').style.display = 'block';
        });
}

function hidePopup() {
    document.querySelector('#popup-overlay').style.display = 'none';
    document.querySelector('#members-popup').style.display = 'none';
}

function showPhotoForm(event_id) {
    fetch(`/event/is_attendee/${event_id}/`)
    .then((response) => response.json())
    .then((data) => {
        if (data.is_attendee) {
            document.querySelector('#popup-overlay-form').style.display = 'block';
            document.querySelector('#photo-form-popup').style.display = 'block';
        }
        else {
            alert("You must be an attendee to post a photo.");
        }
    })
}

function cancelPhotoForm() {
    document.querySelector('#popup-overlay-form').style.display = 'none';
    document.querySelector('#photo-form-popup').style.display = 'none';
}

function initMap() {
    const map_div = document.querySelector('#map');
    if (map_div) {
        const lat = parseFloat(map_div.getAttribute('data-lat'));
        const lng = parseFloat(map_div.getAttribute('data-lng'));
        const map = new google.maps.Map(map_div, {
            center: { lat: lat, lng: lng },
            zoom: 16,
            controlSize: 22,
        });

        const geocoder = new google.maps.Geocoder();
        const infowindow = new google.maps.InfoWindow();
        const latlng = {
            lat: lat,
            lng: lng,
          };


        geocoder.geocode({ location: latlng })
        .then((response) => {
            if (response.results[0]) {
                const address = response.results[0].formatted_address;
                const marker = new google.maps.Marker({
                        position: latlng,
                        map: map,
                        url: `https://www.google.com/maps/search/?api=1&query=${address}`
                });
        
                google.maps.event.addListener(marker, 'click', function() {window.location.href = marker.url;});
        
                    infowindow.setContent(address);
                    infowindow.open(map, marker);
            } 
            else {
              window.alert("No results found");
            }
        })
        .catch((e) => window.alert("Geocoder failed due to: " + e));
    }
}

function load_photos(event_id) {
    const carousel = document.querySelector('#photos_carousel');
    const carouselInner = document.querySelector("#carousel-inner");

    fetch(`/event/get_photos/${event_id}`)
    .then(response => response.json())
    .then(data => {
        data.photos.forEach((url, index) => {
            carouselInner.innerHTML += `
                <img class="carousel-img" src="${url}" alt="Image ${index + 1}" />
            `;
        });   
    })
    .then (() => {
        document.querySelectorAll('#photos_carousel span').forEach(span => {
            span.addEventListener('click', () => {
                const imageWidth = carousel.querySelectorAll("img")[0].clientWidth + 10;
                carouselInner.scrollLeft += span.id == "left" ? -imageWidth : +imageWidth;
            })
        })
    })
}

function deleteEvent (event_id) {
    const confirmMessage = "Are you sure you want to delete this event?";
    if (!confirm(confirmMessage)) {
        return;
    }
    fetch(`/event/delete/${event_id}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': CSRF_TOKEN,
        },
    })
    .then(response => {
        if (response.status === 200) {
            // Request was successful
            window.location.href = '/';
        } else if (response.status === 403) {
            // Permission denied
            alert("Permission Denied");
        }
    })
    .catch(error => {
        console.error(error);
    });
}