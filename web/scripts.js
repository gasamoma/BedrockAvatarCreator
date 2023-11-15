// include https://code.jquery.com/jquery-3.6.0.min.js



$(document).ready(function() {
    //declare the presignedUrlvariable
    let presignedUrl;
    let api_backend_url = "https://a4mqym33sh.execute-api.us-east-1.amazonaws.com/prod/";
    let cognito_url = "https://bedrock-avatar-creator-domain-000001.auth.us-east-1.amazoncognito.com/login?client_id=529e8uqd64sk72n0u4nejthns7&response_type=token&redirect_uri=https://d1sjp6oavn8rzq.cloudfront.net/index.html";
    const loadingOverlay = $("#loading-overlay");
    // get the id="submit-button" element
    const submitButton = $("#submit-button");
    const photoStyles = $("#photo-styles")
    const video = $("#video");
    const customName = $("#custom-name")
    const yoDiv = $("#yo");
    const resetButton = $("#reset")
    resetButton.hide();
    customName.hide();
    yoDiv.hide();
    const styles = [
        { id: 1, name: 'Biologa', image: '', description: 'Biologa' },
        { id: 2, name: 'Quimica', image: '', description: 'Quimica' },
        { id: 3, name: 'Fisica', image: '', description: 'Fisica' },
        { id: 4, name: 'Astronoma', image: '', description: 'Astronoma' },
        { id: 5, name: 'Geologa', image: '', description: 'Geologa' },
        { id: 6, name: 'Ecologa', image: '', description: 'Ecologa' },
        { id: 7, name: 'Microbiologa', image: '', description: 'Microbiologa' },
        { id: 8, name: 'Neurocientifica', image: '', description: 'Neurocientifica' },
        { id: 9, name: 'Genetista', image: '', description: 'Genetista' },
        { id: 10, name: 'Cientifica Ambiental', image: '', description: 'Cientifica Ambiental' },
        { id: 11, name: 'Desarrolladora de Software', image: '', description: 'Desarrolladora de Software' },
        { id: 12, name: 'Cientifica de Datos', image: '', description: 'Cientifica de Datos' },
        { id: 13, name: 'Ingeniera de Redes', image: '', description: 'Ingeniera de Redes' },
        { id: 14, name: 'Analista de Ciberseguridad', image: '', description: 'Analista de Ciberseguridad' },
        { id: 15, name: 'Administradora de Bases de Datos', image: '', description: 'Administradora de Bases de Datos' },
        { id: 16, name: 'Diseñadora UX-UI', image: '', description: 'Diseñadora UX-UI' },
        { id: 17, name: 'Gerente de Proyectos de IT', image: '', description: 'Gerente de Proyectos de IT' },
        { id: 18, name: 'Ingeniera Civil', image: '', description: 'Ingeniera Civil' },
        { id: 19, name: 'Ingeniera Mecanica', image: '', description: 'Ingeniera Mecanica' },
        { id: 20, name: 'Ingeniera Electrica', image: '', description: 'Ingeniera Electrica' },
        { id: 21, name: 'Ingeniera Aeroespacial', image: '', description: 'Ingeniera Aeroespacial' },
        { id: 22, name: 'Ingeniera Biomedica', image: '', description: 'Ingeniera Biomedica' },
        { id: 23, name: 'Ingeniera Ambiental', image: '', description: 'Ingeniera Ambiental' },
        { id: 24, name: 'Matematica', image: '', description: 'Matematica' },
        { id: 25, name: 'Estadistica', image: '', description: 'Estadistica' },
        { id: 26, name: 'Criptografa', image: '', description: 'Criptografa' },
        { id: 27, name: 'Arquitecta', image: '', description: 'Arquitecta' },
        { id: 28, name: 'Cientifica-Investigadora', image: '', description: 'Cientifica/Investigadora' },
        { id: 29, name: 'Diseñadora Grafica', image: '', description: 'Diseñadora Grafica' },
        { id: 30, name: 'Profesora', image: '', description: 'Profesora' },
        { id: 31, name: 'Psicologa', image: '', description: 'Psicologa' },
        { id: 32, name: 'Veterinaria', image: '', description: 'Veterinaria' }
    ];

    // Function to show the loading overlay
    function showLoadingOverlay() {
        loadingOverlay.show();
    }

    // Function to hide the loading overlay
    function hideLoadingOverlay() {
        loadingOverlay.hide();
    }

    function dataURLtoFile(photoDataUrl, filename) {
        // convert the photoDataUrl into a File object
        // photoDataUrl is a base64 encoded string with a (data:image/png;base64,encoded_string) starting the string
        // we need to remove the (data:image/png;base64,encoded_string) part of the string
        photoDataUrl = photoDataUrl.replace(/^data:image\/\w+;base64,/, "");
        // we need to remove the trailing = from the photoDataUrl
        photoDataUrl = photoDataUrl.replace(/=$/, "");
        // we need to convert the photoDataUrl into a Uint8Array
        photoDataUrl = Uint8Array.from(atob(photoDataUrl), c => c.charCodeAt(0));
        // we need to create a new File object with the photoDataUrl and the filename
        // the photoDataUrl is a Uint8Array, so we need to convert it to a Blob
        photoDataUrl = new Blob([photoDataUrl], { type: 'image/png' });
        return new File([photoDataUrl], filename, { type: 'image/png' });
    }

    function uploadFile(signedUrl = "https://some.s3.amazonaws.com/", data = {}) {
        // get the file from the input
        let file;

        if (data != {}) {
            // convert the photoDataUrl into a File object
            const photoFile = dataURLtoFile(data, 'photo.png');
            // set the file to the photoFile
            file = photoFile;

        }
        else {
            // otherwise, use the file from the input
            file = document.getElementById('file').files[0];
        }

        // make a request to the signed url
        $.ajax({
            contentType: 'binary/octet-stream',
            url: signedUrl,
            type: 'PUT',
            data: file,
            processData: false
        });
    }
    hideLoadingOverlay();
    // Call the showLoadingOverlay function when you want to display the overlay
    // Call the hideLoadingOverlay function when your
    function something_failed(jqXHR, textStatus, error) {
        // reload to index.html
        console.log(error);
        window.location.href = "index.html";
        return;
    }
    // a fucntion that does a jquery post
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

    // a fucntion tha does a jquery
    function get(url, headers = {}) {
        let request;
        request = $.ajax({
            timeout: 60000,
            type: 'GET',
            url: url,
            headers: headers
        });
        return request.fail(function(jqXhr, textStatus, errorMessage) {
            something_failed(jqXhr, textStatus, errorMessage);
        });
    }

    function get_presigned_url(id_token) {
        // create a header Authorization with the id_token
        headers = {
            'Authorization': 'Bearer ' + id_token
        }
        // do a get request to this endpoint /get_presigned_url
        return get(api_backend_url + 'api_backend', headers).then(response => {
            // and return the presigned url
            return response;
        });
    }
    // a function that ...
    function submit_button_function(id_token) {
        // show the loading overlay
        showLoadingOverlay();
        headers = {
            'Authorization': 'Bearer ' + id_token
        }

        // get the key and the bucket from the presigned url
        const url_wo_headers = presignedUrl.split("?")[0];
        const splited_url = url_wo_headers.split('/');

        const bucket = splited_url[2];
        const key = splited_url.slice(3, splited_url.length).join("/");
        // call the api_backend_url+'api_backend' post method
        post(api_backend_url + 'api_backend', {
            'bucket': bucket,
            'key': key,
            'styles': $("#photo-styles").val(),
            'custom-name': $("#custom-name").val()
        }, headers).then(response => {
            // create a notification
        });

        createNotification_jquery("Procesing Image");
        console.log("Image Generated")
        hideLoadingOverlay();
        resetButton.show();
        // hide the loading overlay
    }
    // hideLoadingOverlay();
    // a function that loads cognito credentials for an api request
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
    // a function that adds <option value="{name}"> from the styles array to the id="browsers" element
    function addOptions() {
        for (let i = 0; i < styles.length; i++) {
            // add the styles name to the option value <option value="styles.id">styles.name</option>
            // add support for accent in letters
            
            $('#browsers').append(`<option value="` + styles[i].id + `">` + styles[i].name + `</option>`);

        }

    }

    function reset_web_page() {
        window.location.href = "index.html";
    }


    function createNotification(message) {
        const notificationContainer = document.getElementById('notificationContainer');

        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });

        notification.appendChild(closeBtn);
        notificationContainer.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        setTimeout(() => {
            notification.remove();
        }, 10000);
    }

    function createNotification_jquery(message) {
        const notificationContainer = $('#notificationContainer');

        const notification = $('<div>');
        notification.addClass('notification');
        notification.text(message);

        const closeBtn = $('<button>');
        closeBtn.addClass('notification-close');
        closeBtn.text('x');
        closeBtn.click(function() {
            notification.remove();
        });

        notification.append(closeBtn);
        notificationContainer.append(notification);

        setTimeout(() => {
            notification.addClass('show');
        }, 100);

        setTimeout(() => {
            notification.remove();
        }, 10000);
    }


    function dismissAll() {
        const notificationContainer = document.getElementById('notificationContainer');
        notificationContainer.innerHTML = '';
    }

    function dismissAll_jquery() {
        const notificationContainer = $('#notificationContainer');
        notificationContainer.empty();
    }




    // if id_token is present in the query string
    if (window.location.hash.includes('id_token')) {
        // get a pressigned url from the api

        loadCredentials().then(id_token => {
            get_presigned_url(id_token).then(response => {
                // store the presigned url in a global mutable variable
                presignedUrl = response['presigned_url'];
            });
        });
        const video = $('#video')[0];
        const canvas = $('#canvas')[0];
        const videoDiv = $('#video')
        const captureButton = $('#take-photo');
        const iWantbutton = $('#i-want-button');
        const styleInput = $('#photo-styles');
        iWantbutton.hide();
        addOptions();
        styleInput.hide();

        // if $("#avatar-form") on summit do not reload
        $("#avatar-form").submit(function(e) {
            e.preventDefault();
            $("#photo-styles").val();
        });

        // Access the user's camera
        navigator.mediaDevices.getUserMedia({ video: true })
            .then((stream) => {
                video.srcObject = stream;
            })
            .catch((error) => {
                console.error('Error accessing camera:', error);
            });

        resetButton.click(reset_web_page);
        // Capture photo from the video stream
        captureButton.click(function() {
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Convert the canvas content to a data URL and log it
            const photoDataUrl = canvas.toDataURL('image/png');
            uploadFile(presignedUrl, photoDataUrl)
            // make photo-styles show and bigger hiding video capture
            photoStyles.show();
            styleInput.show();
            customName.show();
            videoDiv.hide();
            captureButton.hide();
            iWantbutton.show();
            yoDiv.show();
            // Optional: You can send the data URL to a server for further processing or storage.
        });
        iWantbutton.click(function() {
            loadCredentials().then(id_token => {
                // check if custom-name and photo-styles are not empty
                if ($("#custom-name").val() === "" || $("#photo-styles").val() === "") {
                    // send notification
                    createNotification("Please fill in all fields");
                    return ;
                }
                // do a post with the credentials to the api
                submit_button_function(id_token);
            });
        });
    }
    else {
        window.location.href = cognito_url;
    }

});
