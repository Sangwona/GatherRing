document.addEventListener('DOMContentLoaded', function() {

    const join_btn = document.querySelector('.join_button');
    const request_btn = document.querySelector('.request_button');
    const viewMember_btn = document.querySelector('.view-members-btn');
    const delete_btn = document.querySelector('#btn-delete');

    if (join_btn) {
        join_btn.onclick = joinOrLeaveGroup;
    }
    if (request_btn) {
        request_btn.onclick = createOrDeleteGroupRequest;
    }
    viewMember_btn.onclick = showGroupMembers;

    delete_btn.onclick = deleteGroup;
});

function showGroupMembers(e) {
    const groupID = e.currentTarget.getAttribute('data-members-id');
    fetch(`/group/members/${groupID}/`)
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

function deleteGroup (e) {
    const confirmMessage = "Are you sure you want to delete this group?";
    if (!confirm(confirmMessage)) {
        return;
    }
    const parent_div = e.currentTarget.parentElement;
    const group_id = parent_div.getAttribute('data-group-id');
        fetch(`/group/delete/${group_id}/`, {
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