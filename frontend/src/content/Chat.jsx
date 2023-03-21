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
            waiting_messages: false,
            page: 0,
            content_names: [
                "chat_block",
                "new_user_block",
                "profile_block",
            ],
        }
    }

    receiveMessage = (message) => {
        if (message.type === "send_message") {
            if (message.chat_id === this.state.chat_id) {
                this.appendMessage(message)
                this.check_messages()
                this.set_scroll_to_bottom("messages")
            } else {
                this.setUncheckedMessageAmount(message.chat_id)
            }
        } else if (message.type === "edit_message") {
            if (message.chat_id === this.state.chat_id)
                this.setNewMessageValue(message)
        } else if (message.type === "create_chat") {
            this.addChatButton(message.chat_id, message.chat_name)
        }
    }

    displayButtons = (name) => {
        let edit = name === "edit" ? "flex" : "none"
        let send = name === "send" ? "flex" : "none"
        document.getElementById("send").style.display = send
        document.getElementById("edit").style.display = edit
        document.getElementById("cancel").style.display = edit
    }

    setNewMessageValue = (message) => {
        let message_li = document.getElementById(message.message_id)
        message_li.firstChild.lastChild.textContent = message.value
    }

    appendMessage = (message) => {
        let messages_ul = document.getElementById("messages")
        let message_li = document.createElement("li")
        let message_li_ul = document.createElement("ul")
        let avatar = document.createElement("li")
        let content = document.createElement("li")

        message_li.setAttribute("id", message.id)
        avatar.textContent = `${message.name} ${message.surname}`
        avatar.style.fontWeight = "bold"
        avatar.style.padding = "10px 0 15px 0"
        avatar.style.textAlign = this.state.user_id == message["sender"] ? "left" : "right"
        content.style.textAlign = this.state.user_id == message["sender"] ? "left" : "right"
        content.textContent = message.value

        message_li.onclick = () => {
            this.setState({ "message_id": message.id })
            this.displayButtons("edit")
            document.getElementById("input_text").value = message_li.firstChild.lastChild.textContent
        }

        message_li_ul.appendChild(avatar)
        message_li_ul.appendChild(content)
        message_li.append(message_li_ul)
        if (!this.state.waiting_messages) {
            messages_ul.appendChild(message_li)
        } else {
//             message_li.style.backgroundColor = "#576"
            messages_ul.insertBefore(message_li, messages_ul.firstChild)
        }
    }

    setUncheckedMessageAmount = async (id) => {
        axios.get(`http://127.0.0.1:8000/chat/${id}/unchecked`)
        .then(function(r) {
            let chat_li = document.getElementById(`chat_${id}`)
            let name = chat_li.textContent.split(":")
            chat_li.textContent = `${name[0]}: ${r.data.length === 0 ? 0 : r.data[0].unchecked_messages}`
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
        this.displayButtons("send")
        document.getElementById("input_text").value = ""
    }

    display_content(display_content_name) {
        this.state.content_names.forEach(function (content_name, _) {
            let display = content_name === display_content_name ? "block" : "none"
            let chat_block = document.getElementById(content_name)
            chat_block.style.display = display
        })
    }

    check_if_need_more_messages = () => {
        let messages = document.getElementById("messages")
        if ((messages.scrollTop === 0) && (!this.state.waiting_messages) && (this.state.page > 0)) {
            this.setState({ "waiting_messages": true })
            this.get_messages_in_the_chat_from_db()
        }
    }

    get_messages_in_the_chat_from_db = async () => {
        let messages = await axios.get(`http://127.0.0.1:8000/chat/${this.state.chat_id}?page=${this.state.page}`)
        let messages_ul = document.getElementById("messages")
        let old_scroll_height = messages_ul.scrollHeight
        for (let i = 0; i < messages.data.length; i++) {
            let idx = this.state.waiting_messages ? messages.data.length - i - 1 : i
            this.appendMessage(messages.data[idx])
        }
        messages_ul.scrollTop = messages_ul.scrollHeight - old_scroll_height
        this.setState({ "page": this.state.page + 1 })
        this.setState({ "waiting_messages": false })
    }

    set_scroll_to_bottom = (element_id) => {
        let element = document.getElementById(element_id)
        element.scrollTop = element.scrollHeight
    }

    addChatButton = (chat_id, chat_name) => {
        let chat_li = document.createElement("li")
        let chat_list_ul = document.getElementById("chat_list")
        chat_li.setAttribute("id", `chat_${chat_id}`)
        chat_li.textContent = `${chat_name}: 0`
        chat_li.onclick = () => {
            this.setState({ "waiting_messages": false })
            this.setState({ "page": 0 })
            this.setState({ chat_id: chat_id })
            this.display_content("chat_block")
            let messages = document.getElementById("messages")
            messages.innerHTML = ""
            messages.scrollTop = 0
            this.get_messages_in_the_chat_from_db()
            this.check_messages()
            this.set_scroll_to_bottom("messages")
        }
        chat_list_ul.insertBefore(chat_li, chat_list_ul.lastChild)
        this.setUncheckedMessageAmount(chat_id)
    }

    create_new_chat = async () => {
        let checkboxes = document.getElementById("checkboxes").getElementsByTagName("li")
        let users = []
        for (let i = 0; i < checkboxes.length; i++) {
            if (checkboxes[i].lastChild.checked) {
                users.push(parseInt(checkboxes[i].lastChild.value))
            }
        }
        let message = JSON.stringify({
            "type": "create_chat",
            "value": users,
        })
        this.state.ws.send(message)
    }

    prepare_chat_creation = async () => {
        let response = await axios.get("http://127.0.0.1:8000/auth/api/users")
        let checkboxes = document.getElementById("checkboxes")
        checkboxes.innerHTML = ""
        response.data.forEach(function(user, _) {
            let user_li = document.createElement("li")
            let user_input = document.createElement("input")
            user_input.type = "checkbox"
            user_input.value = user["id"]
            user_input.style.pointerEvents = "none"
            user_li.onclick = () => {
                user_input.checked = !user_input.checked
            }
            user_li.textContent = `${user["name"]} ${user["surname"]}`
            user_li.appendChild(user_input)
            checkboxes.appendChild(user_li)
        })
        this.display_content("new_user_block")
    }

    create_websocket_connection = () => {
//         axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
//         const url = `ws://127.0.0.1:8000/chat/ws`
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
            this.addChatButton(chat.id, chat.name)
        }
    }

    componentWillUnmount() {
        this.state.ws.close()
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
                                <li onClick={this.prepare_chat_creation} >New chat</li>
                            </ul>
                        </li>
                    </ul>

                    <ul id="chat_block" className="block_content">
                         <li>
                            <ul id="messages" onScroll={this.check_if_need_more_messages}>
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
                            <ul id="checkboxes" className="list"></ul>
                            <ul>
                                <div className="send_button" onClick={this.create_new_chat}>Create</div>
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