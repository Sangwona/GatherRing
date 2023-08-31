document.addEventListener('DOMContentLoaded', function() {
    join_btn = document.querySelector('.join_button');
    request_btn = document.querySelector('.request_button');
    if (join_btn) {
        join_btn.onclick = joinOrLeaveEvent;
    }
    if (request_btn) {
        request_btn.onclick = createOrDeleteEventRequest;
    }
});

function joinOrLeaveEvent(e) {
    const event_id = e.currentTarget.getAttribute('data-event-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated == "True") { 
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
    else {
        alert("You must be logged in to join the event.");
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