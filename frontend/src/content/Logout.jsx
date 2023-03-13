import { useNavigate } from "react-router";
import React from "react";

import { removeToken } from "./Auth";


export default function Logout() {
    const navigate = useNavigate()
    const logout = () => {
        removeToken();
        navigate("/")
    }

    return (
        <div>
            <h1>Log Out</h1>
            <button onClick={logout}>Log Out</button>
        </div>
    )
}