import React, {useState} from "react";
import axios from "axios";
import "./css/Register.css";
import {useNavigate} from "react-router";

export default function Register() {
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [name, setName] = useState("");
    const [surname, setSurname] = useState("");

    const register = async (ev) => {
        if ((email === "") || (password === "") || (name === "") || (surname === ""))
            return

        const data = {
            "email": email,
            "password": password,
            "name": name,
            "surname": surname,
        }

        axios.post("http://127.0.0.1:8000/auth/register", data)
            .then(navigate("/login"))
            .catch(err => document.getElementById("status").textContent = err.response.data.detail)
    }
    return (
        <div>
            <h1>Register</h1>
            <div id="register_form">
                <input type="text" placeholder="email" onChange={(e) => setEmail(e.target.value)}/>
                <input type="text" placeholder="password" onChange={(e) => setPassword(e.target.value)}/>
                <input type="text" placeholder="name" onChange={(e) => setName(e.target.value)}/>
                <input type="text" placeholder="surname" onChange={(e) => setSurname(e.target.value)}/>
                <button onClick={register}>register</button>
            </div>
            <div id="status"></div>
        </div>
    )
}