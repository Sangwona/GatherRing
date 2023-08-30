document.addEventListener('DOMContentLoaded', function() {
    join_btn = document.querySelector('.join_button');
    request_btn = document.querySelector('.request_button');
    if (join_btn) {
        join_btn.onclick = joinOrLeaveGroup;
    }
    if (request_btn) {
        request_btn.onclick = createOrDeleteGroupRequest;
    }
});

function joinOrLeaveGroup(e) {
    const group_id = e.currentTarget.getAttribute('data-group-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated == "True") { 
        fetch(`/group/toggle_membership/${group_id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.joined) {
                    join_btn.textContent = "Leave Group";
                }
                else {
                    join_btn.textContent = "Join Group";
                }
                document.querySelector(`.member_count`).textContent = `${data.member_count}`;        
            })
    }
    else {
        alert("You must be logged in to join the group.");
    }
}

function createOrDeleteGroupRequest(e) {
    const group_id = e.currentTarget.getAttribute('data-group-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated == "True") {
        fetch(`/group/toggle_request/${group_id}/`)
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
        alert("You must be logged in to join the group.");
    }
}