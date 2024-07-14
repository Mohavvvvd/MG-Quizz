window.addEventListener("DOMContentLoaded", function() {
  const quizContainer = document.querySelector(".quiz-container");

  document.getElementById("btn").addEventListener("click", function(event) {
    event.preventDefault();
    quizContainer.innerHTML = ""; 
    const n = parseInt(document.getElementById("n").value);
    if (isNaN(n) || n <= 0) {
      alert("Please enter a valid number of questions.");
      return false;
    }
    
    const titleInput = document.getElementById("t");
    if (titleInput.value.trim() == "") {
      alert("Please enter a quiz title.");
      return false;
    }
    
    document.querySelectorAll(".h").forEach(element => {
      element.classList.remove("h");
    });
    
    for (let i = 0; i < n; i++) {
      const quizDiv = document.createElement("div");
      quizDiv.className = "con";

      const questionInput = document.createElement("input");
      questionInput.type = "text";
      questionInput.placeholder = `Enter question ${i + 1}`;
      quizDiv.appendChild(questionInput);

      for (let j = 0; j < 3; j++) {
        const answerInput = document.createElement("input");
        answerInput.type = "text";
        answerInput.placeholder = `Enter answer ${j + 1}`;
        quizDiv.appendChild(answerInput);
      }

      const correctAnswerInput = document.createElement("select");
      correctAnswerInput.innerHTML = `
          <option value="">Select correct answer</option>
          <option value="0">Answer 1</option>
          <option value="1">Answer 2</option>
          <option value="2">Answer 3</option>
      `;
      quizDiv.appendChild(correctAnswerInput);

      quizContainer.appendChild(quizDiv);
    }
  });

  document.getElementById("c").addEventListener("click", function() {
    let questions = [];

    const titleInput = document.getElementById("t");
    const descriptionInput = document.getElementById("d");
    const levelSelect = document.getElementById("s");

    if (titleInput.value.trim() == "" || descriptionInput.value.trim() == "" || levelSelect.value == "") {
        alert("Please fill out all fields.");
        return false;
    }

    for (let i = 0; i < quizContainer.children.length; i++) {
        const questionDiv = quizContainer.children[i];
        const questionInput = questionDiv.querySelector("input[type='text']");
        const answerInputs = questionDiv.querySelectorAll("input[type='text']");
        const correctAnswerInput = questionDiv.querySelector("select");

        const question = questionInput.value;
        const answers = Array.from(answerInputs).slice(1).map(input => input.value);
        const correctAnswer = correctAnswerInput.value;

        if (!question || answers.every(answer => answer.trim() == "") || !correctAnswer) {
            alert("Please fill out all fields for each question.");
            return false;
        }
        questions.push({
            question: question,
            answers: answers,
            correctAnswer: correctAnswer
        });
    }
    questions.unshift({
        title: titleInput.value,
        description: descriptionInput.value,
        level: levelSelect.value
    });

    console.log(JSON.stringify(questions, null, 2));
    
    fetch('/add_question', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify(questions)
  })
  .then(response => response.json())
  .then(data =>{
      console.log(data)
      alert(data.message)
  })
  .catch(error => {
      console.error('Error:', error)
      alert('Error creating question. Please try again.')
  })
});
});