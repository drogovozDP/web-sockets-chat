export function appendMessage(users, message) {
    let messages_ul = document.getElementById("messages")
    let message_li = document.createElement("li")
    message_li.textContent = `${users[message.sender]["name"]} ${users[message.sender]["surname"]}: ${message.value}`
    messages_ul.appendChild(message_li)
    console.log(message)
}
