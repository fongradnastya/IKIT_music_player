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

// Generate a prime number for p
let p = generatePrimeNumber();

// Generate a random number for g
let g = Math.floor(Math.random() * 1000);

// Generate a private key
let privateKey = Math.floor(Math.random() * 1000);

// Calculate the public key
let publicKey = modPow(g, privateKey, p);

// Receive the server's public key (you'll need to implement this part)
let serverPublicKey = receiveServerPublicKey();
console.log(serverPublicKey)

// Compute the shared secret
let sharedSecret = modPow(serverPublicKey, privateKey, p);


function receiveServerPublicKey() {
    return new Promise((resolve, reject) => {
        // The URL of your server
        const url = 'http://127.0.0.1:8000/users/public-key';

        // Create a new XMLHttpRequest object
        let xhr = new XMLHttpRequest();

        // Configure the request
        xhr.open('GET', url, true);

        // Set the callback function
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                // Parse the response as text
                const publicKey = xhr.responseText;

                // Resolve the promise with the public key
                resolve(publicKey);
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

