const form = document.forms.main;
form.addEventListener('submit', (event) => {
    event.preventDefault();
    console.log("submit");
    validateForm();
})

function validateForm(){
    let pass1 = form.password.value;
    let pass2 = form.password_confirm.value;
    if(pass1 === pass2){
        let username = form.username.value;
        let email = form.email.value;
        if(username !== "" && email !== ""){
            getSharedKey().then((key) => {
                console.log('Key' + key);
                convertKey(key).then(({key, iv}) => {
                // Encrypt the text
                    return encrypt("Hello, world!", key, iv).then(encryptedText => {
                        // Decrypt the text
                        return decrypt(encryptedText, key, iv).then(decryptedText => {
                            console.log('Decrypted text:', decryptedText);
                        });
                    });
                }).catch(error => {
                    console.error('An error occurred:', error);
                });
            })
        }
    }
    else{
        console.log("Not correct");
    }
}

// Function to generate a prime number
function generatePrimeNumber() {
    while (true) {
        let primeCandidate = Math.floor(Math.random() * 1000);
        if (isPrime(primeCandidate)) {
            return primeCandidate;
        }
    }
}

// Function to check if a number is prime
function isPrime(num) {
    for(let i = 2; i < num; i++)
        if(num % i === 0) return false;
    return num > 1;
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

function getSharedKey(){
    return receiveServerPublicKey().then(({serverPublicKey, p, q}) => {
        console.log(serverPublicKey, p, q);
        // Compute the shared secret
        let publicKey = 1;
        let sharedSecret = 0;
        let privateKey = 0;
        while(publicKey === 1){
            privateKey = Math.floor(Math.random() * p);
            sharedSecret = modPow(serverPublicKey, privateKey, p);
            publicKey = modPow(q, privateKey, p);
        }
        console.log('Public' + publicKey)
        console.log(sharedSecret);
        return {sharedSecret, publicKey};
    }).then(({sharedSecret, publicKey}) => {
        sendClientPublicKey(publicKey);
        return sharedSecret;
    }).catch((error) => {
        console.error(error)
    });
}

function sendClientPublicKey(publicKey){
    let url = 'http://127.0.0.1:8000/users/receive-public-key';
    let data = {publicKey: publicKey}; // data to be sent to the server

    fetch(url, {
        method: 'POST', // or 'PUT'
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function receiveServerPublicKey() {
    return new Promise((resolve, reject) => {
        // The URL of your server
        const url = 'http://127.0.0.1:8000/users/get-public-key';
        // Create a new XMLHttpRequest object
        let xhr = new XMLHttpRequest();
        // Configure the request
        xhr.open('GET', url, true);
        // Set the callback function
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                // Parse the response as text
                let responseJson = JSON.parse(xhr.responseText);
                let serverPublicKey = responseJson.public_key;
                let p = responseJson.p;
                let q = responseJson.q;
                console.log(serverPublicKey, p, q);
                // Resolve the promise with the public key
                resolve({serverPublicKey, p, q});
            } else {
                // Reject the promise with the status text
                reject(xhr.statusText);
            }
        };
        // Handle network errors
        xhr.onerror = function() {
            reject(xhr.statusText);
        };
        // Send the request
        xhr.send();
    });
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
    console.log(data);
    // Encrypt the data
    const encryptedData = await window.crypto.subtle.encrypt(
        {
            name: 'AES-GCM',
            iv: iv
        },
        key,
        data
    );
    console.log(new Uint8Array(encryptedData));
    const encryptedDataArray = new Uint8Array(encryptedData);
    return btoa(String.fromCharCode.apply(null, encryptedDataArray));
}

async function decrypt(text, key, iv){
    const encryptedDataArray = Uint8Array.from(atob(text), c => c.charCodeAt(0));
    const encryptedData = encryptedDataArray.buffer;
    // Decrypt the data
    const decryptedData = await window.crypto.subtle.decrypt(
        {
            name: 'AES-GCM',
            iv: iv
        },
        key,
        encryptedData
    );
    const decoded = new TextDecoder().decode(decryptedData)
    console.log(decoded);
    return decoded;
}