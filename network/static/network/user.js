document.addEventListener('DOMContentLoaded', function() {
    // Handle like button
    document.querySelectorAll('.like').forEach(button => {
        button.onclick = function(e) {
            e.stopPropagation(); // Prevent the post click event from triggering

            const postId = this.dataset.postId;
            const csrftoken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            fetch(`/posts/${postId}/like`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(result => {
                if (result.error) {
                    alert(result.error);
                } else {
                    // Update the like button color and like count
                    const likeButton = document.querySelector(`svg.like[data-post-id='${postId}']`);
                    const likeCount = document.querySelector(`svg.like[data-post-id='${postId}'] + span`);

                    // Update the like button color based on whether the user liked the post
                    likeButton.style.fill = result.userLiked ? 'red' : 'transparent';
                    // Update the like count
                    likeCount.textContent = result.likes;
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
        };
    });

    // Handle comment submission
    document.querySelectorAll('.comment').forEach(button => {
        button.onclick = function(e) {
            e.stopPropagation(); // Prevent the post click event from triggering

            const postId = this.dataset.postId;

            // Check if a textarea already exists
            if (this.nextElementSibling && this.nextElementSibling.tagName === 'TEXTAREA') {
                return;
            }

            // Create a textarea and submit button
            const textarea = document.createElement('textarea');
            const submitButton = document.createElement('button');
            submitButton.textContent = "Submit";
            submitButton.classList.add('btn', 'btn-primary', 'mt-2');

            // Insert the textarea and button into the DOM
            this.insertAdjacentElement('afterend', textarea);
            textarea.insertAdjacentElement('afterend', submitButton);

            // Hide the comment button while writing a comment
            this.style.display = 'none';

            // Prevent the textarea and button from triggering the post click event
            textarea.addEventListener('click', e => e.stopPropagation());
            submitButton.addEventListener('click', e => e.stopPropagation());

            // Submit button event listener
            submitButton.onclick = function() {
                const commentContent = textarea.value.trim();

                if (commentContent) {
                    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                    fetch(`/posts/${postId}/comment`, {
                        method: 'POST',
                        body: JSON.stringify({ content: commentContent }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.error) {
                            alert(result.error);
                        } else {
                            textarea.remove();
                            submitButton.remove();
                            alert(result.message);
                            button.style.display = 'inline-block';
                        }
                    });
                } else {
                    alert("Comment cannot be empty!");
                }
            };
        };
    });


    // Handle post edit
    document.querySelectorAll('.edit-post').forEach(button => {
        button.onclick = function(e) {
            e.stopPropagation(); // Prevent the post click event from triggering

            const postId = this.dataset.postId;

            // Check if a textarea already exists
            if (this.nextElementSibling && this.nextElementSibling.tagName === 'TEXTAREA') {
                return;
            }

            // Hide the edit button while editing
            this.style.display = 'none';

            // Get the current post content
            const postContentElement = document.querySelector(`div[data-post-id='${postId}'] .post-content`);
            const currentContent = postContentElement.textContent;

            // Create a textarea pre-filled with the current content
            const textarea = document.createElement('textarea');
            textarea.value = currentContent;
            const submitButton = document.createElement('button');
            submitButton.textContent = "Save";
            submitButton.classList.add('btn', 'btn-primary', 'mt-2');

            // Insert the textarea and button into the DOM
            postContentElement.insertAdjacentElement('afterend', textarea);
            textarea.insertAdjacentElement('afterend', submitButton);

            // Prevent the textarea and button from triggering the post click event
            textarea.addEventListener('click', e => e.stopPropagation());
            submitButton.addEventListener('click', e => e.stopPropagation());

            // Submit button event listener
            submitButton.onclick = function() {
                const newContent = textarea.value.trim();

                if (newContent) {
                    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
                    fetch(`/posts/${postId}/edit`, {
                        method: 'PUT',
                        body: JSON.stringify({ content: newContent }),
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': csrfToken
                        }
                    })
                    .then(response => response.json())
                    .then(result => {
                        if (result.error) {
                            alert(result.error);
                        } else {
                            // Update the specific post's content in the DOM
                            postContentElement.textContent = result.content;
                            // Remove the textarea and submit button after successful submission
                            textarea.remove();
                            submitButton.remove();
                            // Re-show the edit button
                            button.style.display = 'inline-block';
                        }
                    });
                } else {
                    alert("Post content cannot be empty!");
                }
            };
        };
    });


    // Make posts clickable, except when clicking on edit, like, or comment buttons
    document.querySelectorAll('.post').forEach(post => {
        post.onclick = function() {
            const postId = this.dataset.postId;
            window.location.href = `/post/${postId}`;
        };
    });

    document.getElementById('follow').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the form from submitting normally

        const button = event.target;
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        const username = this.dataset.username;

        fetch(`/follow/${username}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error){
                alert(data.error);
            }
            else{
            if (data.message === "followed") {
                button.classList.remove('btn-primary');
                button.classList.add('btn-danger');
                button.textContent = "Unfollow";
            } else if (data.message === "unfollowed") {
                button.classList.remove('btn-danger');
                button.classList.add('btn-primary');
                button.textContent = "Follow";
            }

            document.querySelector('.follower-count').textContent = `${data.followers} Followers`;
            document.querySelector('.following-count').textContent = `${data.following} Following`;
        }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });

});
