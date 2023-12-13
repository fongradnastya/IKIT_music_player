const usernameField = $('.user__name');

$(document).ready(function() {
    if(usernameField){
        $('.logout').on('click', logout);
        getPlaylist().then(() => {
            $('.slider').slick({
            slidesToShow: 4,
        });
    });
    }
})

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

async function getPlaylist(){
    let sharedSecret = await generateSharedSecret();
    const url = 'http://127.0.0.1:8000/users/get-home-data'
    let response = await fetch(url, {
        method: 'GET',
        credentials: 'include',  // This is required to send cookies
    });
    let data = await response.json();
    const username = data.username;
    const playlistNames = await JSON.parse(data.playlists);
    if(username){
        const text= base64ToArrayBuffer(username)
        const iv = base64ToArrayBuffer(data.iv);
        let {key, _} = await convertKey(sharedSecret);
        try{
            let name = await decrypt(text, key, iv);
            usernameField.text(name);
        }
        catch(exception){
            console.error(exception);
        }
        let names = [];
        for(let i = 0; i < playlistNames.length; i++) {
            const playlist =
                base64ToArrayBuffer(playlistNames[i]);
            try{
                let name = await decrypt(playlist, key, iv);
                names.push(name);
            }
            catch(exception){
                console.error(exception);
            }
        }
        addPlaylists(names);
    }
    else{
        window.location.href = '/users/login';
    }

}

function addPlaylists(playlists){
    let slider = document.querySelector('.slider');
    slider.innerHTML = '';  // Clear the slider
    for (let playlist of playlists) {
        let item = document.createElement('div');
        item.className = 'slider__item';

        let link = document.createElement('a');
        link.href = '#';
        link.className = 'slider__link';

        let imgDiv = document.createElement('div');
        imgDiv.className = 'img';

        let img = document.createElement('img');
        img.src = '/media/photos/2022/11/07/cover_DGDvHzB.png';
        img.alt = 'new tracks';
        img.className = 'playlist-cover';

        let buttonsDiv = document.createElement('div');
        buttonsDiv.className = 'track__buttons';

        let a = document.createElement('a');
        a.href = '#';

        let firstDiv = document.createElement('div');
        firstDiv.className = 'first-div';
        firstDiv.onclick = function() { $('.first-div > div').toggleClass('pause'); };

        let playButton = document.createElement('div');
        playButton.className = 'track__play play__button';

        let p = document.createElement('p');
        p.textContent = playlist;
        // Append elements
        firstDiv.appendChild(playButton);
        a.appendChild(firstDiv);
        buttonsDiv.appendChild(a);
        imgDiv.appendChild(img);
        imgDiv.appendChild(buttonsDiv);
        link.appendChild(imgDiv);
        link.appendChild(p);
        item.appendChild(link);
        slider.appendChild(item);
    }
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

async function generateSharedSecret(){
    const p = 23;
    const q = 5;
    const privateKey = Math.floor(Math.random() * p);
    const publicKey = modPow(q, privateKey, p);
    await sendClientPublicKey(publicKey);
    const {serverPublicKey, a, b} = await receiveServerPublicKey();
    const sharedSecret = modPow(serverPublicKey, privateKey, p);
    console.log(p, q, privateKey, publicKey, sharedSecret);
    return sharedSecret;

}
async function receiveServerPublicKey() {
    // The URL of your server
    const url = '/users/get-public-key';
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

async function sendClientPublicKey(publicKey){
    let url = '/users/count-keys';
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
    return decoded;
}