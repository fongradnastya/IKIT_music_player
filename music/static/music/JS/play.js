let current_song = null

const player = document.querySelector(".play-track"),
    playBtn = document.querySelector(".play__pause"),
    prevBtn = document.querySelector(".play__previous"),
    nextBtn = document.querySelector(".play__next"),
    audio = document.querySelector(".audio"),
    progressConteiner = document.querySelector(".play__progress"),
    progress = document.querySelector(".play__curr-progress"),
    name = document.querySelector(".play__name"),
    author = document.querySelector(".play__author"),
    cover = document.querySelector(".play__image img")

function playSong(){
    player.classList.add("play")
    audio.play()
}

function stopSong(){
    player.classList.remove("play")
    audio.pause()
}

function play(){
    const isPlaying = player.classList.contains("play")
    if (isPlaying) {
        stopSong()
    }else{
        playSong()
    }
}

document.addEventListener("DOMContentLoaded", play)

playBtn.addEventListener("click", play)

function updateProgress(e){
    const duration = audio.duration
    const currentTime = audio.currentTime
    const progressPercent = (currentTime / duration) * 100
    progress.style.width = `${progressPercent}%`

}

audio.addEventListener("timeupdate", updateProgress)

function setProgress(e){
    const width = this.clientWidth
    const clickX = e.offsetX
    const duration = audio.duration
    console.log((clickX / width) * duration)
    audio.onprogress = function() {
        audio.currentTime = (clickX / width) * duration;
    };
    console.log(audio.currentTime)
}

progressConteiner.addEventListener("click", setProgress)

function nextSong(){
    nextItem = document.querySelector(".play__next")
    console.log(nextItem.getAttribute("href"))
    window.location.href = nextItem.getAttribute("href")
}

audio.addEventListener("ended", nextSong)


