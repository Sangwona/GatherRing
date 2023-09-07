document.addEventListener('DOMContentLoaded', function() {
    const group_id = document.querySelector('#button-div').getAttribute('data-group-id');
    const user_is_authenticated = document.querySelector('#button-div').getAttribute('data-is-authenticated');

    const join_btn = document.querySelector('.join_button');
    const request_btn = document.querySelector('.request_button');
    const delete_btn = document.querySelector('#btn-delete');

    if (join_btn) {
        join_btn.addEventListener('click', () => joinOrLeaveGroup(group_id, user_is_authenticated));
    }
    if (request_btn) {
        request_btn.addEventListener('click', () => createOrDeleteGroupRequest(group_id, user_is_authenticated));
    }
    if (delete_btn) {
        cancel_btn.addEventListener('click', (e) => deleteGroup(e, group_id))
    }

    document.querySelector('.view-members-btn').addEventListener('click', () => showGroupMembers(group_id));
    document.querySelector('.photo_upload_button').addEventListener('click', () => showPhotoForm(group_id));
    document.querySelector('#cancel_form').addEventListener('click', cancelPhotoForm);

    load_photos(group_id);
});

function joinOrLeaveGroup(group_id, user_is_authenticated) {
    if (user_is_authenticated == "True") { 
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

function createOrDeleteGroupRequest(group_id, user_is_authenticated) {
    if (user_is_authenticated == "True") {
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

function deleteGroup (e, group_id) {
    const confirmMessage = "Are you sure you want to delete this group?";
    if (!confirm(confirmMessage)) {
        return;
    }
    
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

function showGroupMembers(group_id) {
    fetch(`/group/members/${group_id}/`)
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

function showPhotoForm(group_id) {
    fetch(`/group/is_member/${group_id}/`)
    .then((response) => response.json())
    .then((data) => {
        if (data.is_member) {
            document.querySelector('#popup-overlay-form').style.display = 'block';
            document.querySelector('#photo-form-popup').style.display = 'block';
        }
        else {
            alert("You must be a member to post a photo.");
        }
    })
}

function cancelPhotoForm() {
    document.querySelector('#popup-overlay-form').style.display = 'none';
    document.querySelector('#photo-form-popup').style.display = 'none';
}

function load_photos(group_id) {
    const carousel = document.querySelector('#photos_carousel');
    const carouselInner = document.querySelector("#carousel-inner");

    fetch(`/group/get_photos/${group_id}`)
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