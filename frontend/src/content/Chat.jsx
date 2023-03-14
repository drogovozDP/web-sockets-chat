import React from "react";
import axios from "axios";
import {fetchToken, setToken} from "./Auth";
import "./css/Chat.css";

export default class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            message_id: 0,
            chat_id: 0,
            content_names: [
                "chat_block",
                "new_user_block",
                "profile_block",
            ]
        }
    }

    receiveMessage = (message) => {
        if (message.type === "send_message") {
            if (message.chat_id === this.state.chat_id) {
                this.appendMessage(message)
                this.check_messages()
            } else {
                this.setUncheckedMessageAmount(message.chat_id)
            }
        } else if (message.type === "edit_message") {
//             let r = await axios.get("http://127.0.0.1:8000/auth/api/users/me",
//                 {"accept": "application/json"})
//             document.getElementById(message.message_id)
//                 .textContent = `${message.name} ${message.surname}: ${message.value}`
        }
    }

    appendMessage = (message) => {
        let messages_ul = document.getElementById("messages")
        let message_li = document.createElement("li")
        message_li.setAttribute("id", message.id)
        message_li.textContent = `${message.name} ${message.surname}: ${message.value}`
        message_li.onclick = () => {
            this.setState({ "message_id": message.id })
            document.getElementById("send").style.display = "none"
            document.getElementById("edit").style.display = "flex"
            document.getElementById("cancel").style.display = "flex"
        }
        messages_ul.appendChild(message_li)

    }


    setUncheckedMessageAmount = async (id) => {
        axios.get(`http://127.0.0.1:8000/chat/${id}/unchecked`)
        .then(function(r) {
            let chat_li = document.getElementById(`chat_${id}`)
            let name = chat_li.textContent.split(":")
            chat_li.textContent = `${name[0]}: ${r.data.length == 0 ? 0 : r.data[0].unchecked_messages}`
        })
    }

    check_messages = () => {
        let message = JSON.stringify({
            "type": "check_message",
            "chat_id": this.state.chat_id,
        })
        this.state.ws.send(message)
        let chat_li = document.getElementById(`chat_${this.state.chat_id}`)
        let name = chat_li.textContent.split(":")
        chat_li.textContent = `${name[0]}: 0`
    }


    sendMessage = () => {
        let textbox = document.getElementById("input_text")
        let message = JSON.stringify({
            "type": "send_message",
            "chat_id": this.state.chat_id,
            "value": textbox.value,
        })
        this.state.ws.send(message)
        textbox.value = ""
    }

    editMessage = async () => {
        let textbox = document.getElementById("input_text")
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        const r = await axios.get("http://127.0.0.1:8000/auth/api/users/me",
            {"accept": "application/json"})
        let message = JSON.stringify({
            "type": "edit_message",
            "chat_id": this.state.chat_id,
            "message_id": this.state.message_id,
            "value": textbox.value,
        })
        this.state.ws.send(message)
        textbox.value = ""
        this.cancelEdit()
    }

    cancelEdit = () => {
        this.setState({ "message_id": 0 })
        document.getElementById("send").style.display = "flex"
        document.getElementById("edit").style.display = "none"
        document.getElementById("cancel").style.display = "none"
    }

    componentWillUnmount() {
        this.state.ws.close()
    }

    display_content(display_content_name) {
        this.state.content_names.forEach(function (content_name, _) {
            let display = content_name === display_content_name ? "block" : "none"
            let chat_block = document.getElementById(content_name)
            chat_block.style.display = display
        })
    }

    async create_new_chat() {
        let checkboxes = document.getElementById("checkboxes").getElementsByTagName("li")
        let users = []
        for (let i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].lastChild.checked) {
                users.push(parseInt(checkboxes[i].lastChild.value))
            }
        }
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`

        // add new chat to the chat list
        let response = await axios.post("http://127.0.0.1:8000/chat", users )
        let chat_li = document.createElement("li")
        let chat_list_ul = document.getElementById("chat_list")
        chat_li.textContent = response.data.chat_details.chat_name
        chat_list_ul.insertBefore(chat_li, chat_list_ul.lastChild)
    }

    create_websocket_connection = () => {
        const url = `ws://127.0.0.1:8000/chat/ws/${this.state.user_id}`
        const ws = new WebSocket(url)
        ws.onmessage = async (ev) => {
            let message = JSON.parse(ev.data)
            this.receiveMessage(message)
        };
        this.setState({ "ws": ws })
    }


    async componentDidMount() {
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        const r = await axios.get("http://127.0.0.1:8000/auth/api/users/me",
            {"accept": "application/json"})
        this.setState({ "user_id": r.data.id })

        this.create_websocket_connection()

        let chat_response = await axios.get("http://127.0.0.1:8000/chat")
        let chat_list = document.getElementById("chat_list")
        for (let i = 0; i < chat_response.data.length; i++) {
            let chat = chat_response.data[i]
            let chat_li = document.createElement("li")
            chat_li.textContent = `${chat.name}: 0`
            chat_li.setAttribute("id", `chat_${chat.id}`)
            this.setUncheckedMessageAmount(chat.id)
            chat_li.onclick = async () => {
                this.setState({ chat_id: chat.id })
                this.display_content("chat_block")
                this.check_messages()

                // add messages from current chat.
                let messages = await axios.get(`http://127.0.0.1:8000/chat/${chat.id}`)
                let messages_ul = document.getElementById("messages")
                messages_ul.innerHTML = ""
                for (let i = 0; i < messages.data.length; i++) {
                    this.appendMessage(messages.data[i])
                }
            }
            chat_list.appendChild(chat_li)
        }

        // 'create new chat' button.
        let new_chat_li = document.createElement("li")
        new_chat_li.textContent = "New chat"
        new_chat_li.onclick = async () => {
            let response = await axios.get("http://127.0.0.1:8000/auth/api/users")
            let checkboxes = document.getElementById("checkboxes")
            response.data.forEach(function(user, _) {
                let user_li = document.createElement("li")
                let user_input = document.createElement("input")
                user_input.type = "checkbox"
                user_input.value = user["id"]
                user_li.textContent = `${user["name"]} ${user["surname"]}`
                user_li.appendChild(user_input)
                checkboxes.appendChild(user_li)
            })
            this.display_content("new_user_block")
        }
        chat_list.appendChild(new_chat_li)
    }

    render() {
        return (
            <div id="Chat">
                <h1 style={{ textAlign: "center" }}>Chat</h1>
                <nav>
                    <ul>
                        <li>
                            <ul id="chat_list_header" className="list_header"><h3>Chat list</h3></ul>
                        </li>
                        <li>
                            <ul id="chat_list" className="list">
                                {/*<li>chat</li>*/}
                            </ul>
                        </li>
                    </ul>

                    <ul id="chat_block" className="block_content">
                         <li>
                            <ul id="messages">
                                {/*<li>message</li>*/}
                            </ul>
                        </li>
                        <li>
                            <textarea id="input_text" placeholder="This is the default text"></textarea>
                            <button id="send" className="send_button" onClick={this.sendMessage}>SEND</button>
                            <button id="edit" className="send_button" onClick={this.editMessage}>EDIT</button>
                            <button id="cancel" className="send_button" onClick={this.cancelEdit}>CANCEL</button>
                        </li>
                    </ul>
                    <ul id="new_user_block" className="block_content">
                        <ul>
                            <ul id="checkboxes"></ul>
                            <ul>
                                <button onClick={this.create_new_chat}>Create</button>
                            </ul>
                        </ul>
                    </ul>
                    <ul id="profile_block" className="block_content">
                    </ul>

                    <ul>
                        <li>
                            <ul id="users_list_header" className="list_header"><h3>User list</h3></ul>
                        </li>
                        <li>
                            <ul id="users_list" className="list">
                                {/*<li>user</li>*/}
                            </ul>
                        </li>
                    </ul>
                </nav>
            </div>
        )
    }
}