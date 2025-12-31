function initVoiceControls(textElementId, playBtnId, pauseBtnId, stopBtnId, langSelectId){
    const textEl = document.getElementById(textElementId);
    if(!textEl) return;

    const langSelect = document.getElementById(langSelectId);
    let currentLang = langSelect ? langSelect.value : 'en-US';

    const playBtn = document.getElementById(playBtnId);
    const pauseBtn = document.getElementById(pauseBtnId);
    const stopBtn = stopBtnId ? document.getElementById(stopBtnId) : null;

    let utterance = null;

    function getVoice(lang){
        const voices = window.speechSynthesis.getVoices();
        // Try exact match
        let voice = voices.find(v => v.lang === lang);
        if(!voice){
            // Try partial match (e.g., 'ta' for Tamil)
            voice = voices.find(v => v.lang.startsWith(lang.split('-')[0]));
        }
        if(!voice){
            // Fallback to English
            voice = voices.find(v => v.lang.startsWith('en')) || voices[0];
        }
        return voice;
    }

    function speakText(){
        if(speechSynthesis.speaking){
            speechSynthesis.resume(); // resume if paused
            return;
        }
        utterance = new SpeechSynthesisUtterance(textEl.innerText);
        utterance.lang = currentLang;
        utterance.rate = 1;
        utterance.pitch = 1;
        utterance.voice = getVoice(currentLang);
        window.speechSynthesis.cancel(); // stop any previous speech
        window.speechSynthesis.speak(utterance);
    }

    function pauseText(){
        if(speechSynthesis.speaking) speechSynthesis.pause();
    }

    function stopText(){
        if(speechSynthesis.speaking) speechSynthesis.cancel();
    }

    if(playBtn) playBtn.addEventListener('click', speakText);
    if(pauseBtn) pauseBtn.addEventListener('click', pauseText);
    if(stopBtn) stopBtn.addEventListener('click', stopText);

    if(langSelect){
        langSelect.addEventListener('change', ()=>{
            currentLang = langSelect.value;
            if(speechSynthesis.speaking){
                stopText(); // stop current speech when language changes
            }
        });
    }

    // Load voices (needed for some browsers)
    if (typeof speechSynthesis !== 'undefined') {
        speechSynthesis.onvoiceschanged = () => {
            // Preload voices
            getVoice(currentLang);
        };
    }
}
