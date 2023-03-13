import React from "react";
import { ws } from "./App"
import axios from "axios";
import {fetchToken} from "./Auth";


export default class Profile extends React.Component {
    constructor(props) {
        super(props);
        this.state = {

        }
    }

    componentDidMount = async () => {
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        const r = await axios.get("http://127.0.0.1:8000/auth/api/users/me",
            {"accept": "application/json"})
        this.display_current_user(r.data.name, r.data.surname)
    }

    display_current_user = (name, surname) => {
        document.getElementById("profile").textContent = `Hello, ${name} ${surname}!`
    }

    render() {
        return (
            <div>
                <h1 id="profile"></h1>
            </div>
        )
    }
}