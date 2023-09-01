document.addEventListener('DOMContentLoaded', function() {

    join_btn = document.querySelector('.join_button');
    request_btn = document.querySelector('.request_button');
    if (join_btn) {
        join_btn.onclick = joinOrLeaveGroup;
    }
    if (request_btn) {
        request_btn.onclick = createOrDeleteGroupRequest;
    }

    document.querySelectorAll('.view-members-btn').forEach(btn => {
        btn.addEventListener('click', showGroupMembers);
    });
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