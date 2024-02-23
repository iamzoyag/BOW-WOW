const startBtn = document.querySelector('.start-btn');
const popupInfo = document.querySelector('.popup-info');
const exitBtn = document.querySelector('.exit-btn');
const main = document.querySelector('.main');
const continueBtn = document.querySelector('.continue-btn');
const quizSection = document.querySelector('.quiz-section');
const quizBox = document.querySelector('.quiz-box');

startBtn.onclick = () => {
    popupInfo.classList.add('active');
    main.classList.add('active');
}

exitBtn.onclick = () => {
    popupInfo.classList.remove('active');
    main.classList.remove('active');
}

continueBtn.onclick = () => {
    quizSection.classList.add('active');
    popupInfo.classList.remove('active');
    main.classList.remove('active');
    quizBox.classList.add('active');
}

let questionCount = 0;

const nextBtn = document.querySelector('.next-btn');

const optionList = document.querySelector('.options');

nextBtn.onclick = () => {
    if(questionCount < questions.length - 1){
        questionCount++;
        showQuestions(questionCount);
    }
    else{
        console.log('Questions completed');
    }
}

function showQuestions(index){
    const questionText = document.querySelector('.question-text');
    questionText.textContent = `${questions[index].numb}. ${questions[index].question}`;

    let optionTag = `<div class="option"><span>${questions[index].options[0]}</span></div>`

    optionList.innerHTML = optionTag;
}

function questionCounter(index){
    const questionTotal = document.querySelector('.question-total');
    questionTotal.textContent = `${index} of ${questions.length} Questions`;
    bottomQuestionCounter.innerHTML = totalQuestionCountTag;
}