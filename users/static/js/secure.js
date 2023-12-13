const registrationForm = document.forms.registration;
const loginForm = document.forms.login;
const creationForm = document.forms.create;
const usernameField = $('.user__name');

if(registrationForm){
    registrationForm.addEventListener('submit', (event) => {
        event.preventDefault();
        validateRegistration();
    })
}
else if(loginForm){
    loginForm.addEventListener('submit', (event) => {
        event.preventDefault();
        validateLogin();
    })
}
else if(creationForm){
    $(document).ready(function() {
        $('.logout').on('click', logout);
        getName();
    });
    creationForm.addEventListener('submit', (event) => {
        event.preventDefault();
        validatePlaylist();
    })
}

async function validatePlaylist(){
    const name = creationForm.name.value;
    const description = creationForm.description.value;
    let playlist = (name === "") ? "Playlist name can't be empty" : "";
    $('.name-error').text(playlist);
    let desc = (description === "") ? "Description can't be empty" : "";
    $('.description-error').text(desc);
    if(name !== '' && description !== ''){
        try {
            let sharedKey = await getSharedKey();
            console.log('Key' + sharedKey);
            let {key, iv} = await convertKey(sharedKey);
            // Encrypt the text
            await sendPlaylistData(name, description, key, iv);
        } catch(error) {
            console.error('An error occurred:', error);
        }
    }
}

async function validateLogin(){
    const username = loginForm.username.value;
    const password = loginForm.password.value;
    let user = (username === "") ? "Username can't be empty" : "";
    $('.username-error').text(user);
    let pass = (password === "") ? "Password can't be empty" : "";
    $('.password-error').text(pass);
    if(username !== "" && password !== ""){
        try {
            let sharedKey = await getSharedKey();
            let {key, iv} = await convertKey(sharedKey);
            // Encrypt the text
            await sendLoginData(username, password, key, iv);
        } catch(error) {
            console.error('An error occurred:', error);
        }
    }
}

async function generateSharedSecret(){
    const p = 23;
    const q = 5;
    const privateKey = Math.floor(Math.random() * p);
    const publicKey = modPow(q, privateKey, p);
    await sendClientPublicKey(publicKey, true);
    const {serverPublicKey, a, b} = await receiveServerPublicKey(true);
    const sharedSecret = modPow(serverPublicKey, privateKey, p);
    console.log(p, q, privateKey, publicKey, sharedSecret);
    return sharedSecret;
}

async function validateRegistration(){
    let pass1 = registrationForm.password.value;
    let pass2 = registrationForm.passwordConfirm.value;
    if(pass1 === pass2){
        $('.error').text("");
        let username = registrationForm.username.value;
        let email = registrationForm.email.value;
        let mail = (email === "") ? "Email can't be empty" : "";
        $('.email-error').text(mail);
        let user = (username === "") ? "Username can't be empty" : "";
        $('.username-error').text(user);
        let pass = (pass1 === "") ? "Password can't be empty" : "";
        $('.password-error').text(pass);
        let conf = (pass2 === "") ? "Password can't be empty" : "";
        $('.confirm-error').text(conf);
        if(username !== "" && email !== ""){
            try {
                let sharedKey = await getSharedKey();
                let {key, iv} = await convertKey(sharedKey);
                // Encrypt the text
                await sendRegistrationData(key, iv);
            } catch(error) {
                console.error('An error occurred:', error);
            }
        }
    }
    else{
        $('.error').text("Passwords don't mach");
    }
}

async function getName(){
    const sharedSecret = await generateSharedSecret();
    const url = 'http://127.0.0.1:8000/users/get-username'
    let response = await fetch(url, {
        method: 'GET',
        credentials: 'include',  // This is required to send cookies
    });
    let data = await response.json();
    const username = data.username;
    if(username){
        const text = base64ToArrayBuffer(username)
        const iv = base64ToArrayBuffer(data.iv);
        let {key, _} = await convertKey(sharedSecret);
        try{
            let name = await decrypt(text, key, iv);
            usernameField.text(name);
        }
        catch(exception){
            console.error(exception);
        }
    }
    else{
        window.location.href = '/users/login';
    }
}

async function sendPlaylistData(name, description, key, iv){
    let encryptedName = await encrypt(name, key, iv);
    let encryptedDescription = await encrypt(description, key, iv);
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        name: encryptedName,
        description: encryptedDescription
    };
    const response = await fetch('/users/receive-playlist', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    const newData = await response.json();
    if (newData.status === 'success') {
        window.location.href = '/users';
    }
    else{
        $('.error').text(newData.error);
        console.log(newData.error);
    }
}

async function sendLoginData(username, password, key, iv){
    let encryptedName = await encrypt(username, key, iv);
    let encryptedPassword = await encrypt(password, key, iv);
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        username: encryptedName,
        password: encryptedPassword
    };
    const response = await fetch('/users/receive-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    const newData = await response.json();
    if (newData.status === 'success') {
        console.log('Success:', newData);
        console.log('Session ID:', getCookie('sessionid'));
        window.location.href = '/users';
    }
    else{
        $('.error').text(newData.error);
        console.log(newData.error);
    }
}

function getCookie(name){
    let cookieArr = document.cookie.split(";");
    for(let i = 0; i < cookieArr.length; i++) {
        let cookiePair = cookieArr[i].split("=");
        if(name === cookiePair[0].trim()) {
            return decodeURIComponent(cookiePair[1]);
        }
    }
    return null;
}

async function sendRegistrationData(key, iv){
    let username = registrationForm.username.value;
    let email = registrationForm.email.value;
    let password = registrationForm.password.value;
    // Encrypt the data
    let encryptedName = await encrypt(username, key, iv);
    let encryptedEmail = await encrypt(email, key, iv);
    let encryptedPassword = await encrypt(password, key, iv);
    // Prepare the data to send to the server
    let data = {
        iv: btoa(String.fromCharCode.apply(null, iv)),
        username: encryptedName,
        email: encryptedEmail,
        password: encryptedPassword
    };
    const response = await fetch('/users/receive-registration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    const newData = await response.json();
    if (data.status === 'success') {
        window.location.href = '/users/login';
    }
    else{
        $('.error').text(newData.error);
        console.log(newData.error);
    }
}

// Function to perform modular exponentiation
function modPow(base, exponent, modulus) {
    if (modulus === 1) return 0;
    let result = 1;
    base = base % modulus;
    while (exponent > 0) {
        if (exponent % 2 === 1) {
            result = (result * base) % modulus;
        }
        exponent = exponent >> 1;
        base = (base * base) % modulus;
    }
    return result;
}

function countSharedSecret(serverPublicKey, p, q) {
    let publicKey = 1;
    let sharedSecret = 0;
    let privateKey = 0;
    while(publicKey === 1){
        privateKey = Math.floor(Math.random() * p);
        sharedSecret = modPow(serverPublicKey, privateKey, p);
        // sharedSecret = 100;
        publicKey = modPow(q, privateKey, p);
    }
    console.log(p, q, privateKey, publicKey, sharedSecret);
    return {sharedSecret, publicKey}
}

async function getSharedKey(){
    try {
        let {serverPublicKey, p, q} = await receiveServerPublicKey();
        console.log(serverPublicKey, p, q);
        let {sharedSecret, publicKey} =
            countSharedSecret(serverPublicKey, p, q);
        await sendClientPublicKey(publicKey);
        return sharedSecret;
    } catch(error) {
        console.error(error);
    }
}

async function sendClientPublicKey(publicKey, is_done=false){
    let url = "";
    if(is_done){
        url = '/users/count-keys';
    }
    else{
        url = '/users/receive-public-key';
    }

    let data = {publicKey: publicKey}; // data to be sent to the server

    // Send the data to the server
    let response = await fetch(url, {
        method: 'POST', // or 'PUT'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error('Network response was not ok');
    }

    let responseData = await response.json();
    console.log('Success:', responseData);
}

async function receiveServerPublicKey(is_done=false) {
    // The URL of your server
    let url = '';
    if(is_done){
        url = '/users/get-public-key';
    }
    else{
        url = '/users/generate-public-key';
    }
    try {
        let response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let responseJson = await response.json();
        let serverPublicKey = responseJson.public_key;
        let p = 23;
        let q = 5;
        // Return the public key
        return {serverPublicKey, p, q};
    } catch (error) {
        console.error('An error occurred:', error);
    }
}

async function convertKey(secretKey){
    const encoder = new TextEncoder();
    const secretKeyBuffer = encoder.encode(secretKey);

    // Hash the secret key
    const hashedKey = await window.crypto.subtle.digest('SHA-256', secretKeyBuffer);

    // Import the hashed key as a CryptoKey
    const key = await window.crypto.subtle.importKey(
        'raw',
        hashedKey,
        'AES-GCM',
        false,
        ['encrypt', 'decrypt']
    );
    const iv = window.crypto.getRandomValues(new Uint8Array(12));
    return {key, iv};
}

async function encrypt(text, key, iv) {
    // The data to encrypt
    const data = new TextEncoder().encode(text);

    // Encrypt the data
    const encryptedData = await window.crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: iv
        },
        key,
        data
    );

    // Convert the encrypted data (including the tag) to a Base64 string
    const encryptedDataArray = new Uint8Array(encryptedData);
    return btoa(String.fromCharCode.apply(null, encryptedDataArray));
}

function base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64);
    const len = binaryString.length;
    const bytes = new Uint8Array(len);
    for (let i = 0; i < len; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
}

async function decrypt(text, key, iv){
    // Decode the Base64 string back into an ArrayBuffer
    const encryptedData = new Uint8Array(text);;

    // Separate the encrypted data and the tag
    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
        {
            name: 'AES-GCM',
            iv: iv,
        },
        key,
        encryptedData.buffer
    );

    const decoded = new TextDecoder().decode(decryptedData);
    console.log(decoded);
    return decoded;
}

async function logout(){
    const response = await fetch('/users/logout', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Assuming you have a function to get cookies
        },
        credentials: 'include'  // To include cookies in the request
    })
    const data = await response.json()
    if (data.status === 'success') {
        console.log('Logged out successfully');
        window.location.href = '/users/login';
    } else {
        console.error('Logout failed:', data.error);
    }
}