const usernameField = $('.user__name');
console.log(usernameField);

$(document).ready(function() {
    if(usernameField){
        $('.logout').on('click', logout);
        getUsername().then(() => {
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

async function getUsername(){
    const url = 'http://127.0.0.1:8000/users/get-username'
    let response = await fetch(url, {
        method: 'GET',
        credentials: 'include',  // This is required to send cookies
    });
    let data = await response.json();
    console.log(data);
    const username = data.username;
    const playlists = await JSON.parse(data.playlists);
    console.log('Playlists ' + playlists);
    console.log('Username ' + username);
    if(username){
        console.log(username);
        const text = base64ToArrayBuffer(username)
        const iv = base64ToArrayBuffer(data.iv);
        const p = data.p;
        const q = data.q;
        const serverPublicKey = data.publicKey;
        let {sharedSecret, publicKey} =
            countSharedSecret(serverPublicKey, p, q);
        let {key, _} = await convertKey(sharedSecret);
        try{
            let name = await decrypt(text, key, iv);
            console.log(name);
            usernameField.text(name);
        }
        catch(exception){
            console.error(exception);
        }
    }
    else{
        window.location.href = '/users/login';
    }
    addPlaylists(playlists);
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
        link.id = playlist.id;

        let imgDiv = document.createElement('div');
        imgDiv.className = 'img';

        let img = document.createElement('img');
        img.src = '/media/' + playlist.fields.cover;
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
        p.textContent = playlist.fields.name;
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
    console.log(encryptedData);
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