
function displayPhrases(phrases) {
    window.phrases = phrases
    window.container = document.getElementsByClassName("container")[0]
    window.currentScore = 0
    window.total = window.phrases.length
    if(showRandom()) {
        showRandomQuestion();
    }
    else {
        drawAllQuestions()
    }
    attachEvents()
}

function showRandomQuestion() {
    var randomPhraseIndex = Math.floor((Math.random() * window.phrases.length));
    drawQuestion(window.phrases[randomPhraseIndex]);
    window.phrases.splice(randomPhraseIndex, 1);
    window.container.innerHTML += buttonsTemplate()

    document.getElementsByClassName("incorrect")[0].addEventListener("click", nextRandomQuestion)
    document.getElementsByClassName("correct")[0].addEventListener("click", score)

}

function score() {
    window.currentScore += 1
    nextRandomQuestion()
}

function nextRandomQuestion() {
    if(window.phrases.length == 0){
        window.container.innerHTML = `<h2 class="english_question">Score ` + window.currentScore + `/` + window.total + `</h2>`
    }
    else {
        window.container.innerHTML = ""
        showRandomQuestion()
        attachEvents()
    }
}

function showRandom() {
    const urlParams = new URLSearchParams(window.location.search)
    const myParam = urlParams.get('myParam')
    return urlParams.has('r')
}

function drawAllQuestions() {
    for(phrase of window.phrases) {
        drawQuestion(phrase)
    }
}

function drawQuestion(phrase) {
    if(phrase.answer_seb) {
        window.container.innerHTML = window.container.innerHTML + bigTemplate()
            .replace("[[english_question]]", phrase.english_question)
            .replace("[[question]]", phrase.question)
            .replace("[[answer_seb]]", phrase.answer_seb)
            .replace("[[answer_frances]]", phrase.answer_frances)
    }
    else if(phrase.french) {
        window.container.innerHTML = window.container.innerHTML + smallTemplate()
            .replace("[[english]]", phrase.english)
            .replace("[[french]]", phrase.french)
    }
    else {
        window.container.innerHTML = window.container.innerHTML + titleTemplate()
            .replace("[[title]]", phrase.title)
    }
}

function attachEvents() {
    for(let speakButton of document.getElementsByClassName("speak-button")) {
        speakButton.addEventListener("click", speakAnswer);
    }

    for(let visibilityButton of document.getElementsByClassName("toggle-visability")) {
        visibilityButton.addEventListener("click", toggleVisability);
    }
}

function toggleVisability(event) {
    const element = event.target.getAttribute("data-element");
    const parent = event.target.parentElement
    let text = parent.getElementsByClassName(element)[0]

    text.style.visibility = text.style.visibility == "visible" ? "hidden" : "visible";
}

function speakAnswer(event) {
    speak(getText(event))
}

function getText(event) {
    const element = event.target.getAttribute("data-text");
    const parent = event.target.parentElement

    return parent.getElementsByClassName(element)[0].innerHTML

}
// https://stackoverflow.com/questions/51904607/ios-safari-speechsynthesisutterance-can-not-set-language
function speak(text) {
    let utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'fr-FR'
    utterance.voice = window.speechSynthesis.getVoices().find((voice) => voice.lang === 'fr-FR')
    speechSynthesis.speak(utterance)
}



function bigTemplate() {
    return  `<div class="phrase">
        <h2 class="english_question">[[english_question]]</h2>
        
        <p class="question">[[question]]</p>
        <button class="speak-button" data-text="question">Speak Question</button>
        <button class="toggle-visability" data-element="question">Show Question</button>

        <p class="answer-seb">[[answer_seb]]</p>
        <button class="speak-button" data-text="answer-seb">Speak Seb Answer</button>
        <button class="toggle-visability" data-element="answer-seb">Show Seb Answer</button>
        
        <p class="answer-frances">[[answer_frances]]</p>
        <button class="speak-button" data-text="answer-frances">Speak Frances Answer</button>
        <button class="toggle-visability" data-element="answer-frances">Show Frances Answer</button>
    </div>`
}

function smallTemplate() {
    return  `<div class="phrase">
        <h2 class="english_question">[[english]]</h2>
        
        <p class="question">[[french]]</p>
        <button class="speak-button" data-text="question">Speak French</button>
        <button class="toggle-visability" data-element="question">Show French</button>
    </div>`
}

function titleTemplate() {
    return  `<h1>[[title]]</h1>`
}

function buttonsTemplate() {
    return  `
    <button class="incorrect">Incorrect</button>
    <button class="correct">Correct</button>`
}