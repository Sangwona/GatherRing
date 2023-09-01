document.addEventListener('DOMContentLoaded', function() {
    join_btn = document.querySelector('.join_button');
    request_btn = document.querySelector('.request_button');
    if (join_btn) {
        join_btn.onclick = joinOrLeaveEvent;
    }
    if (request_btn) {
        request_btn.onclick = createOrDeleteEventRequest;
    }
    document.querySelectorAll('.view-members-btn').forEach(btn => {
        btn.addEventListener('click', showEventAttendees);
    });
});

function showEventAttendees(e) {

    const eventID = e.currentTarget.getAttribute('data-members-id');
    fetch(`/event/attendees/${eventID}/`)
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

function joinOrLeaveEvent(e) {
    const event_id = e.currentTarget.getAttribute('data-event-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated != "True") { 
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

function createOrDeleteEventRequest(e) {
    const event_id = e.currentTarget.getAttribute('data-event-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated == "True") {
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
    else {
        alert("You must be logged in to join the event.");
    }
}