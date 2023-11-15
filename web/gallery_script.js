$(document).ready(function() {
    let api_backend_url = "https://a4mqym33sh.execute-api.us-east-1.amazonaws.com/prod/";
    let cognito_url = "https://bedrock-avatar-creator-domain-000001.auth.us-east-1.amazoncognito.com/login?client_id=529e8uqd64sk72n0u4nejthns7&response_type=token&redirect_uri=https://d1sjp6oavn8rzq.cloudfront.net/index.html";
    const logoNav = $("#nav-logo");
    function something_failed(jqXHR, textStatus, error) {
        // reload to index.html
        console.log(error);
        const hash_parameters = window.location.hash
        
        window.location.href = "index.html" + hash_parameters;
        return;
    }
    function home_web_page() {
        // navigate to gallery.html and forward hash string parameters
        // get the all the hash string paremeters using jquery
        const hash_parameters = window.location.hash
        
        window.location.href = "index.html" + hash_parameters;
    }

    function post(url, data, headers = {}) {
        // 60 second timeout
        let request;
        request = $.ajax({
            timeout: 60000,
            type: 'POST',
            url: url,
            data: JSON.stringify(data),
            dataType: 'json',
            headers: headers
        });
        return request.fail(function(jqXhr, textStatus, errorMessage) {
            something_failed(jqXhr, textStatus, errorMessage);
        });
    }

    function get_user_files(id_token) {
        // create a header Authorization with the id_token
        headers = {
            'Authorization': 'Bearer ' + id_token
        }
        // do a get request to this endpoint /get_user_files
        return post(api_backend_url + "get_user_files", {}, headers).then(response => {
            // and return the presigned url
            const imageUrls = response;

            const galleryContainer = document.getElementById('galleryContainer');

            // Dynamically create thumbnail elements
            imageUrls.forEach((imageUrl, index) => {
                const thumbnail = document.createElement('div');
                thumbnail.className = 'thumbnail blur';

                const img = document.createElement('img');
                img.src = imageUrl["url"];
                img.alt = `Image ${index + 1}`;

                thumbnail.appendChild(img);
                galleryContainer.appendChild(thumbnail);
            });
            const blurSwitch = $('#blurSwitch');
            const imageGallery = $('.thumbnail');
            
            // set blur by default
            blurSwitch.checked = true;
            // do the same but wiht jquery
            blurSwitch.change(function () {
                if (this.checked) {
                    imageGallery.addClass('blur');
                } else {
                    imageGallery.removeClass('blur');
                }
            });
            // trigger the blur by default
            blurSwitch.click();
            // if thumbnail is clicked, remove blur for that image
            imageGallery.click(function () {
                // if does not contain blur class, remove blur if not add it
                if (!$(this).hasClass('blur')) {
                    $(this).addClass('blur');
                }else{
                    $(this).removeClass('blur');
                }
            });
        });
    }

    function loadCredentials() {
        return new Promise((resolve, reject) => {
            // get the id_token from the query string
            const id_token = window.location.hash.match(/id_token=([^&]+)/);
            // check if id_token has [1] index
            if (typeof id_token[1] === 'undefined') {
                reject(cognito_url);
            }
            // otherwise, resolve with the id_token
            resolve(id_token[1]);
        });
    }
    
    logoNav.click(home_web_page);
    loadCredentials().then(id_token => {
        get_user_files(id_token);
    });

});
