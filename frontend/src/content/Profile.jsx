import React from "react";
import axios from "axios";
import {fetchToken} from "./Auth";


export default class Profile extends React.Component {
    constructor(props) {
        super(props);
        this.state = {

        }
    }

    componentDidMount = () => {
        axios.defaults.headers.common['Authorization'] = `Bearer ${fetchToken()}`
        axios.get("http://127.0.0.1:8000/auth/api/users/me",
            {
                "accept": "application/json",
            })
            .then(response => this.display_current_user(response.data))
    }

    display_current_user = (data) => {
        document.getElementById("profile").textContent = `Hello, ${data.name} ${data.surname}!`
    }

    render() {
        return (
            <div>
                <h1 id="profile"></h1>
            </div>
        )
    }
}