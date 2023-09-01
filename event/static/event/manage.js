document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.handle_request_btn').forEach((button) => {
        button.onclick = handleRequest;
    })
});

function handleRequest(e) {
    var parent_div = e.currentTarget.parentElement;
    var request_id = parent_div.getAttribute('data-request-id');

        fetch(`/event/handle_request/${request_id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN,
            },
            body: JSON.stringify({
                'action': e.currentTarget.classList.contains('accept') ? 'accept' : 'reject'
            })
        })
        .then(response => {
            if (response.status === 201) {
                // Request was successful
                parent_div.remove()
            } else if (response.status === 403) {
                // Permission denied
                alert("Permission Denied");
            }
        })
        .catch(error => {
            console.error(error);
        });
}