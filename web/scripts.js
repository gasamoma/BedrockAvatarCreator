// include https://code.jquery.com/jquery-3.6.0.min.js



$(document).ready(function() {
    //declare the presignedUrlvariable
    let presignedUrl;
    let api_backend_url = "{replace_with_api_back_rul}";
    let cognito_url = "{replace_with_cognito_url}";
    const loadingOverlay = $("#loading-overlay");
    // get the id="submit-button" element
    const submitButton = $("#submit-button");
    const styles = [
        { id: 1, name: 'Medico', image: '', description: 'Medico', },
		{ id: 2, name: 'Enfermero/a', image: '', description: 'Enfermero/a', },
		{ id: 3, name: 'Maestro/Profesor', image: '', description: 'Maestro/Profesor', },
		{ id: 4, name: 'Ingeniero', image: '', description: 'Ingeniero', },
		{ id: 5, name: 'Abogado', image: '', description: 'Abogado', },
		{ id: 6, name: 'Contador', image: '', description: 'Contador', },
		{ id: 7, name: 'Policia', image: '', description: 'Policia', },
		{ id: 8, name: 'Chef/Cocinero', image: '', description: 'Chef/Cocinero', },
		{ id: 9, name: 'Piloto', image: '', description: 'Piloto', },
		{ id: 10, name: 'Soldado', image: '', description: 'Soldado', },
		{ id: 11, name: 'Programador/Desarrollador de software', image: '', description: 'Programador/Desarrollador de software', },
		{ id: 12, name: 'Secretario/Asistente', image: '', description: 'Secretario/Asistente', },
		{ id: 13, name: 'Conductor/Repartidor', image: '', description: 'Conductor/Repartidor', },
		{ id: 14, name: 'Dependiente/Vendedor', image: '', description: 'Dependiente/Vendedor', },
		{ id: 15, name: 'Electricista', image: '', description: 'Electricista', },
		{ id: 16, name: 'Plomero', image: '', description: 'Plomero', },
		{ id: 17, name: 'Mecanico', image: '', description: 'Mecanico', },
		{ id: 18, name: 'Constructor/Albañil', image: '', description: 'Constructor/Albañil', },
		{ id: 19, name: 'Peluquero/Barbero', image: '', description: 'Peluquero/Barbero', },
		{ id: 20, name: 'Psicologo', image: '', description: 'Psicologo', },
		{ id: 21, name: 'Periodista', image: '', description: 'Periodista', },
		{ id: 22, name: 'Diseñador Grafico', image: '', description: 'Diseñador Grafico', },
		{ id: 23, name: 'Agricultor', image: '', description: 'Agricultor', },
		{ id: 24, name: 'Cartero', image: '', description: 'Cartero', },
		{ id: 25, name: 'Recepcionista', image: '', description: 'Recepcionista', },
		{ id: 26, name: 'Camarero/Mesero', image: '', description: 'Camarero/Mesero', },
		{ id: 27, name: 'Contador', image: '', description: 'Contador', },
		{ id: 28, name: 'Analista financiero', image: '', description: 'Analista financiero', },
		{ id: 29, name: 'Gerente de proyectos', image: '', description: 'Gerente de proyectos', },
		{ id: 30, name: 'Consultor', image: '', description: 'Consultor', },
		{ id: 31, name: 'Enfermero/a', image: '', description: 'Enfermero/a', },
		{ id: 32, name: 'Fisioterapeuta', image: '', description: 'Fisioterapeuta', },
		{ id: 33, name: 'Veterinario', image: '', description: 'Veterinario', },
		{ id: 34, name: 'Cientifico/Investigador', image: '', description: 'Cientifico/Investigador', },
		{ id: 35, name: 'Economista', image: '', description: 'Economista', },
		{ id: 36, name: 'Arquitecto', image: '', description: 'Arquitecto', }]

    // Function to show the loading overlay
    function showLoadingOverlay() {
        loadingOverlay.show();
    }

    // Function to hide the loading overlay
    function hideLoadingOverlay() {
        loadingOverlay.hide();
    }
    function uploadFile(signedUrl="https://some.s3.amazonaws.com/") {
        // get the file from the input
        const file = $("#image-upload")[0].files[0];
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
    
    // a fucntion that does a jquery post
    function post(url, data, headers={}) {
        return $.ajax({
            type: 'POST',
            url: url,
            data: JSON.stringify(data),
            dataType: 'json',
            headers: headers
            }
        );
    }
    // a fucntion tha does a jquery get.
    function get(url, headers={}) {
        return $.ajax({
            type: 'GET',
            url: url,
            headers: headers
        });
    }
    // a function that ...
    function get_presigned_url(id_token) {
        // create a header Authorization with the id_token
        headers = {
            'Authorization': 'Bearer ' + id_token
        }
        // do a get request to this endpoint /get_presigned_url
        return get(api_backend_url, headers).then(response => {
            // and return the presigned url
            return response;
        });
    }
    // a function that ...
    function submit_button_function(id_token){
        // show the loading overlay
        showLoadingOverlay();
        // hideLoadingOverlay();
    }
    // a function that loads cognito credentials for an api request
    function loadCredentials() {
        return new Promise((resolve, reject) => {
            // get the id_token from the query string
            const id_token = window.location.hash.match(/id_token=([^&]+)/);
            // check if id_token has [1] index
            if(typeof id_token[1] === 'undefined') {
                //reject(cognito_url);
            }
            // otherwise, resolve with the id_token
            resolve(id_token[1]);
        });
    }
    // a function that adds <option value="{name}"> from the styles array to the id="browsers" element
    function addOptions() {
        for (let i = 0; i < styles.length; i++) {
            // add the styles name to the option value <option value="styles.id">styles.name</option>
            $('#browsers').append(`<option value="`+styles[i].id+`">`+styles[i].name+`</option>`);
            
        }
        
    }
            
            
        
    
    
    // if id_token is present in the query string
    if (true){//window.location.hash.includes('id_token')) {
        // get a pressigned url from the api
        
        // loadCredentials().then(id_token => {
        //     get_presigned_url(id_token).then(response => {
        //         // store the presigned url in a global mutable variable
        //         presignedUrl = response;
        //     });
        // });
        const video = $('#video')[0];
        const canvas = $('#canvas')[0];
        const captureButton = $('#capture');
        addOptions();
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
        
        // Capture photo from the video stream
        captureButton.click(function() {
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert the canvas content to a data URL and log it
            const photoDataUrl = canvas.toDataURL('image/png');
            console.log('Captured Photo:', photoDataUrl);
            uploadFile()
            
            // Optional: You can send the data URL to a server for further processing or storage.
        });
        submitButton.click(function() {
            loadCredentials().then(id_token => {
                // do a post with the credentials to the api
                submit_button_function(id_token);
            });
        });
    }else {
        //window.location.href = cognito_url;
    }

});
