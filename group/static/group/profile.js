document.addEventListener('DOMContentLoaded', function() {
    join_btn = document.querySelector('.join_button');
    if (join_btn) {
        join_btn.onclick = joinGroup;
    }

});

function joinGroup(e) {
    const group_id = e.currentTarget.getAttribute('data-group-id');
    const is_authenticated = e.currentTarget.getAttribute('data-is-authenticated');

    if (is_authenticated == "True") {
        if (e.currentTarget.classList.contains('request')) {
            fetch(`/group/request/${group_id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.requested) {
                    document.querySelector(`.join_button`).textContent = "Withdraw Request";
                }
                else {
                    document.querySelector(`.join_button`).textContent = "Request to Join";
                }
            })
        }
        else {  
            fetch(`/group/join/${group_id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.joined) {
                    document.querySelector(`.join_button`).textContent = "Leave Group";
                }
                else {
                    document.querySelector(`.join_button`).textContent = "Join Group";
                }
                document.querySelector(`.member_count`).textContent = `${data.member_count}`;        
            })
        }
    }
    else {
        alert("You must be logged in to join the group.");
    }
}