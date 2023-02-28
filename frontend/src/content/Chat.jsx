import React from "react";
import axios from "axios";
import { fetchToken, RequireToken } from "./Auth";
import "./css/Chat.css";


export default class Chat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            // chat_list: [],
        }
    }
    componentDidMount() {
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        axios.get("http://127.0.0.1:8000/chat")
            .then(function (r){
                let chat_list = document.getElementById("chat_list")
                // for (let i = 0; i < 10; i++)
                r.data.forEach(function (chat, index) {
                    let chat_li = document.createElement("li")
                    chat_li.textContent = chat.name
                    chat_li.onclick = () => {
                        axios.get(`http://127.0.0.1:8000/chat/${chat.id}`)
                            .then(function(r) {
                                let chat = document.getElementById("chat")
                                chat.innerHTML = ""
                                r.data.forEach(function(message, index) {
                                    let message_li = document.createElement("li")
                                    message_li.textContent = `${message.sender}: ${message.value}`
                                    chat.appendChild(message_li)
                                })
                            })
                    }
                    chat_list.appendChild(chat_li)
                })
            })
    }

    render() {
        return (
            <div id="Chat">
                <h1 style={{textAlign: "center"}}>Chat List</h1>
                <nav>
                    <ul id="chat_list"></ul>
                    <ul id="chat">
                        <li>ПРивет</li>
                        <li>ПРивет</li>
                    </ul>
                </nav>
            </div>
        )
    }
}