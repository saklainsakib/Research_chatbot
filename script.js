const chat = document.getElementById("chat");
const input = document.getElementById("message");
const send = document.getElementById("send");
const newChat = document.getElementById("newChat");

let history = [];


function addMessage(role, text) {

    const welcome = document.querySelector(".welcome");

    if (welcome) {
        welcome.remove();
    }

    const message = document.createElement("div");

    message.className = "message";

    message.innerHTML = `
        <div class="avatar">
            ${role === "user" ? "U" : "R"}
        </div>

        <div class="message-body">
            <div class="role">
                ${role === "user" ? "You" : "ResearchBot"}
            </div>

            <div class="content"></div>
        </div>
    `;

    const content = message.querySelector(".content");

    // Render Markdown properly
    if (role === "assistant") {
        content.innerHTML = marked.parse(text);
    } else {
        content.textContent = text;
    }

    chat.appendChild(message);

    chat.scrollTop = chat.scrollHeight;
}


async function sendMessage() {

    const text = input.value.trim();

    if (!text) {
        return;
    }

    input.value = "";

    addMessage("user", text);

    send.disabled = true;

    try {

        const response = await fetch("/api/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                message: text,
                history: history
            })
        });


        const data = await response.json();


        if (!response.ok) {

            addMessage(
                "assistant",
                data.error || "Something went wrong."
            );

            return;
        }


        addMessage(
            "assistant",
            data.answer
        );


        history.push({
            role: "user",
            content: text
        });

        history.push({
            role: "assistant",
            content: data.answer
        });


    } catch (error) {

        addMessage(
            "assistant",
            "Could not connect to the server."
        );

        console.error(error);

    } finally {

        send.disabled = false;

        input.focus();
    }
}


send.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keydown",
    function(event) {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();
        }
    }
);


document.addEventListener(
    "click",
    function(event) {

        const button =
            event.target.closest(".topic");

        if (!button) {
            return;
        }

        input.value =
            button.dataset.question;

        input.focus();
    }
);


newChat.addEventListener(
    "click",
    function() {

        history = [];

        chat.innerHTML = `
            <div class="welcome">

                <div class="icon">
                    🔬
                </div>

                <h2>What would you like to research?</h2>

                <p>
                    Ask a research question and ResearchBot
                    will generate a structured response.
                </p>

            </div>
        `;

        input.focus();
    }
);