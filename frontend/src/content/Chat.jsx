import React from "react";
import axios from "axios";
import {fetchToken, setToken} from "./Auth";
import "./css/Chat.css";
// import { ws } from "./App"
import { appendMessage, setUncheckedMessageAmount } from "./ChatUtils";


export default class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            content_names: [
                "chat_block",
                "new_user_block",
                "profile_block",
            ]
        }
    }

    sendMessage = () => {
        let text = document.getElementById("input_text").value
        let message = JSON.stringify({
            "type": "send_message",
            "chat_id": this.state.chat_id,
            "value": text,
        })
        this.state.ws.send(message)
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


    async componentDidMount() {
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        const r = await axios.get("http://127.0.0.1:8000/auth/api/users/me",
            {"accept": "application/json"})
        this.setState({ "user_id": r.data.id })
        const url = `ws://127.0.0.1:8000/chat/ws/${this.state.user_id}`
        const ws = new WebSocket(url)
        ws.onmessage = (ev) => {
            let message = JSON.parse(ev.data)
            console.log(message)
            if (message.type === "send_message") {
                appendMessage(this.state.users, message)
            } else if (message.type === "notification") {
                setUncheckedMessageAmount(message.chat_id, message.message_amount)
            }

        };
        this.setState({ "ws": ws })

        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        let chat_response = await axios.get("http://127.0.0.1:8000/chat")
        let chat_list = document.getElementById("chat_list")
        for (let i = 0; i < chat_response.data.length; i++) {
            let chat = chat_response.data[i]
            let chat_li = document.createElement("li")
            chat_li.textContent = `${chat.name}: 0`
            chat_li.setAttribute("id", `chat_${chat.id}`)
            chat_li.onclick = async () => {
                this.setState({ chat_id: chat.id })
                let message = JSON.stringify({
                    "type": "select_chat",
                    "value": chat.id,
                })
                this.state.ws.send(message)
                this.display_content("chat_block")
                setUncheckedMessageAmount(chat.id, 0)

                // set new user's names and surnames.
                let user_names = await axios.get(`http://127.0.0.1:8000/chat/${chat.id}/users`)
                let users = {}
                user_names.data.forEach(function(user, _) {
                    users[user["id"]] = {"name": user["name"], "surname": user["surname"]}
                })
                this.setState({ "users": users })

                // add messages from current chat.
                let messages = await axios.get(`http://127.0.0.1:8000/chat/${chat.id}`)
                let messages_ul = document.getElementById("messages")
                messages_ul.innerHTML = ""
                // for (let i = 0; i < 10; i ++)
                for (let i = 0; i < messages.data.length; i++) {
                    appendMessage(this.state.users, messages.data[i])
                }
            }
            chat_list.appendChild(chat_li)
        }

        // set unchecked messages
        let unchecked_messages_response = await axios.get("http://127.0.0.1:8000/chat/unchecked")
        for (let i = 0; i < unchecked_messages_response.data.length; i++) {
            let unchecked_chat = unchecked_messages_response.data[i]
            setUncheckedMessageAmount(
                unchecked_chat.chat_id,
                unchecked_chat.unchecked_messages
            )

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
                            <button onClick={this.sendMessage}>SEND</button>
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