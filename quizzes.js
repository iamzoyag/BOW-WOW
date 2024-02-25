const questions = [
    {
      question: "What is the fundamental principle behind the concept of sampling with replacement?",
      options: [" Objects are chosen without regard to their category", "Each selection reduces the number of available objects for subsequent selections",
       "Once an object is chosen, it is returned to the pool of available objects", 
       "Objects are selected based on a predetermined order"],
      answer: " Once an object is chosen, it is returned to the pool of available objects"
    },
    {
      question: "In the context of binary relations, what does it mean for a relation to be reflexive?",
      options: ["It satisfies the transitive property", "It includes every possible pair of elements",
      "Every element is related to itself", 
      "It is symmetric across the diagonal"],
      answer: "Every element is related to itself"
    },
    {
      question: "What does the concept of 'degree' refer to in the context of multivariate polynomials?",
      options: ["The number of terms in the polynomial", "The highest power of any variable in the polynomial",
      "The total number of variables in the polynomial", 
      "The coefficient of the leading term"],
      answer: "The highest power of any variable in the polynomial"
    },
    {
        question: "How does the concept of self-loops impact the construction of graphs?",
        options: [" It limits the number of edges in the graph", "It allows vertices to be connected to themselves",
        "It ensures that all vertices have the same degree", 
        "It prohibits the formation of cycles in the graph"],
        answer: "It allows vertices to be connected to themselves"
    },
    {
        question: "In the context of selection problems, what does it mean for order to matter?",
        options: ["The arrangement of selected objects is significant", " Objects are chosen randomly",
        "The selection process is repeated multiple times", 
        "Objects are chosen without regard to their category"],
        answer: "The arrangement of selected objects is significant"
    }
  ];
  
let currentQuestion = 0;
let score = 0;

const questionText = document.getElementById("question-text");
const optionsContainer = document.getElementById("options-container");
const submitBtn = document.getElementById("submit-btn");
const resultContainer = document.getElementById("result-container");

function showQuestion() {
  const currentQuestionData = questions[currentQuestion];
  questionText.textContent = currentQuestionData.question;
  optionsContainer.innerHTML = "";
  currentQuestionData.options.forEach(option => {
    const button = document.createElement("button");
    button.textContent = option;
    button.classList.add("quiz-option");
    button.addEventListener("click", function() {
      selectOption(option);
    });
    optionsContainer.appendChild(button);
  });
}

let selectedOption = null;

function selectOption(option) {
  selectedOption = option;
}

function checkAnswer() {
  if (!selectedOption) {
    alert("Please select an option");
    return;
  }
  if (selectedOption === questions[currentQuestion].answer) {
    score++;
  }
  currentQuestion++;
  if (currentQuestion < questions.length) {
    showQuestion();
  } else {
    showResult();
  }
}

function showResult() {
  questionText.textContent = "";
  optionsContainer.innerHTML = "";
  submitBtn.style.display = "none";
  resultContainer.textContent = `Your score: ${score}/${questions.length}`;
}

submitBtn.addEventListener("click", checkAnswer);

showQuestion();
