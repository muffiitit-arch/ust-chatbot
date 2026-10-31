const chatBox = document.getElementById("chatBox");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const clearBtn = document.getElementById("clearBtn");
const suggestionBtns = document.querySelectorAll(".suggestion-btn");

const welcomeMessage = `
    <div class="message bot-message">
        <div class="bubble">
            <p>السلام عليكم ورحمة الله<br>أنا مساعد تسجيل، اكتب استفسارك وسأحاول مساعدتك</p>
        </div>
    </div>
`;

function linkify(text) {
    return text.replace(
        /(https?:\/\/[^\s<]+)|((?:reg|support|ustgate)\.[a-z0-9.-]+\.[a-z]{2,}(?:\/[^\s<]*)?)/g,
        function (match, fullUrl, bareDomain) {
            const url = fullUrl ? fullUrl : "https://" + bareDomain;
            return '<a href="' + url + '" target="_blank" rel="noopener" class="chat-link">' + match + "</a>";
        }
    );
}

function showTyping() {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", "bot-message");
    wrapper.id = "typing-indicator";
    wrapper.innerHTML = `
        <div class="typing-dots">
            <span></span><span></span><span></span>
        </div>
    `;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) indicator.remove();
}

function addMessage(text, sender) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", sender === "user" ? "user-message" : "bot-message");
    const content = sender === "bot" ? linkify(text) : text;
    wrapper.innerHTML = `<div class="bubble"><p>${content}</p></div>`;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function splitQuestions(text) {
    text = text.trim();

    let parts = text.split(/[؟?،,\n\r]+|\.\s+/)
        .map(s => s.trim())
        .filter(s => s.length > 2);

    if (parts.length > 1) {
        return parts;
    }

    const questionWords = [
        "كيف", "ما", "ماذا", "ايش", "إيش", "كم", "متى", "امتى", "إمتى",
        "أين", "اين", "وين", "فين", "هل", "من", "مين",
        "ليش", "ليه", "لماذا", "عايز", "اريد", "داير", "ابغى", "أبغى"
    ];

    const pattern = new RegExp("\\s+و?(" + questionWords.join("|") + ")\\s+", "g");

    let marked = text.replace(pattern, "|$1 ");

    parts = marked.split("|")
        .map(s => s.trim())
        .map(s => s.replace(/\s+و\s*$/, "").trim())
        .filter(s => s.length > 2);

    return parts.length > 1 ? parts : [text];
}

function askServer(question) {
    return fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json());
}

function sendQuestion() {
    const text = userInput.value.trim();
    if (text === "") return;

    addMessage(text, "user");
    userInput.value = "";

    const questions = splitQuestions(text);

    showTyping();

    let chain = Promise.resolve();
    const delay = 700;

    questions.forEach((q, index) => {
        chain = chain.then(() => {
            return askServer(q).then(data => {
                return new Promise(resolve => {
                    setTimeout(() => {
                        if (index === questions.length - 1) {
                            removeTyping();
                        }
                        addMessage(data.answer, "bot");
                        resolve();
                    }, delay);
                });
            });
        });
    });

    chain.catch(error => {
        setTimeout(() => {
            removeTyping();
            addMessage("حدث خطأ أثناء الاتصال بالمساعد", "bot");
        }, 700);
        console.error(error);
    });
}

clearBtn.addEventListener("click", function () {
    chatBox.innerHTML = welcomeMessage;
});

sendBtn.addEventListener("click", sendQuestion);

userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") sendQuestion();
});

suggestionBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
        userInput.value = btn.textContent;
        sendQuestion();
    });
});