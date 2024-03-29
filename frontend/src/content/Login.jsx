import { useNavigate } from "react-router";
import { fetchToken, setToken } from "./Auth";
import React, { useState } from "react";
import "./css/Login.css"
import axios from "axios";
import { URL } from "./App.jsx"

export default function Login() {
    const navigate = useNavigate();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const login = () => {
        if ((username === "") || (password === ""))
            return

        const data = new URLSearchParams();
        data.append("username", username);
        data.append("password", password);
        const requestOptions = {
            method: "POST",
            headers: {
                "accept": "application/json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: data,
        }

        axios.post(`${URL}/auth/token`, data, requestOptions)
            .then(function (response) {
                if (response.data.access_token) {
                    setToken(response.data.access_token);
                    navigate("/profile");
                }
            })
            .catch(r => document.getElementById("status").textContent = r.response.data.detail)
    };

    return (
        <div>
            <h1>login page</h1>
            <div>
                {fetchToken() ? (
                    <p>You are logged in</p>
                ) : (
                    <div>
                        <div id="login_form">
                            <input
                                type="text"
                                placeholder="email"
                                onChange={(e) => setUsername(e.target.value)}
                            />
                            <input
                                type="password"
                                placeholder="password"
                                onChange={(e) => setPassword(e.target.value)}
                            />
                            <button onClick={login}>Login</button>
                        </div>
                        <div id="status"></div>
                    </div>
                )}
            </div>
        </div>
    );
}
