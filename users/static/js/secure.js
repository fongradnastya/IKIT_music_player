const registrationForm = document.forms.registration;
const loginForm = document.forms.login;
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

$(document).ready(function() {
    if(usernameField){
        getUsername()
    }
})

async function validateLogin(){
    const username = loginForm.username.value;
    const password = loginForm.password.value;
    if(username !== "" && password !== ""){
        try {
            let sharedKey = await getSharedKey();
            console.log('Key' + sharedKey);
            let {key, iv} = await convertKey(sharedKey);
            // Encrypt the text
            await sendLoginData(username, password, key, iv);
        } catch(error) {
            console.error('An error occurred:', error);
        }
    }
}

async function validateRegistration(){
    let pass1 = registrationForm.password.value;
    let pass2 = registrationForm.password_confirm.value;
    if(pass1 === pass2){
        let username = registrationForm.username.value;
        let email = registrationForm.email.value;
        if(username !== "" && email !== ""){
            try {
                let sharedKey = await getSharedKey();
                console.log('Key' + sharedKey);
                let {key, iv} = await convertKey(sharedKey);
                // Encrypt the text
                await sendRegistrationData(key, iv);
            } catch(error) {
                console.error('An error occurred:', error);
            }
        }
    }
    else{
        console.log("Not correct");
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
    fetch('http://127.0.0.1:8000/users/receive-login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        // If the user was created successfully, redirect to the login page
        if (data.status === 'success') {
            console.log('Success:', data);
            console.log('Session ID:', getCookie('sessionid'));
            window.location.href = 'http://127.0.0.1:8000/users';
            //getHomePage();
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}

function getCookie(name) {
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
        iv: btoa(String.fromCharCode.apply(null, iv)), // Convert the IV to a Base64 string
        username: encryptedName,
        email: encryptedEmail,
        password: encryptedPassword
    };

    // Send the data to the server
    fetch('http://127.0.0.1:8000/users/receive-registration', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    }).then(data => {
        console.log('Success:', data);
        // If the user was created successfully, redirect to the login page
        if (data.status === 'success') {
            window.location.href = '/users/login';
        }
    }).catch(error => {
        console.error('Error:', error);
    });
}

async function getUsername(){
    const url = 'http://127.0.0.1:8000/users/get-username'
    let response = await fetch(url, {
        method: 'GET',
        credentials: 'include',  // This is required to send cookies
    });
    let data = await response.json();
    console.log(data);
    console.log(data.username);
    usernameField.text(data.username);
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
        //sharedSecret = modPow(serverPublicKey, privateKey, p);
        sharedSecret = 100;
        publicKey = modPow(q, privateKey, p);
    }
    console.log('Public' + publicKey)
    console.log(sharedSecret);
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

async function sendClientPublicKey(publicKey){
    let url = 'http://127.0.0.1:8000/users/receive-public-key';
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

async function receiveServerPublicKey() {
    // The URL of your server
    const url = 'http://127.0.0.1:8000/users/get-public-key';
    try {
        let response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        let responseJson = await response.json();
        let serverPublicKey = responseJson.public_key;
        let p = responseJson.p;
        let q = responseJson.q;
        console.log(serverPublicKey, p, q);
        // Return the public key
        return {serverPublicKey, p, q};
    } catch (error) {
        console.error('An error occurred:', error);
    }
}


async function convertKey(secretKey){
    console.log('Started');
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
    console.log(key);
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
    console.log(encryptedDataArray)
    return btoa(String.fromCharCode.apply(null, encryptedDataArray));
}

async function decrypt(text, key, iv){
    // Decode the Base64 string back into an ArrayBuffer
    const encryptedDataWithTagArray = Uint8Array.from(atob(text), c => c.charCodeAt(0));

    // Separate the encrypted data and the tag
    const encryptedDataArray = encryptedDataWithTagArray.slice(0, -16);
    const tagArray = encryptedDataWithTagArray.slice(-16);

    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
        {
            name: 'AES-GCM',
            iv: iv,
            additionalData: tagArray.buffer
        },
        key,
        encryptedDataArray.buffer
    );

    const decoded = new TextDecoder().decode(decryptedData);
    console.log(decoded);
    return decoded;
}