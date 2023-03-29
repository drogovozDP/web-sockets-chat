import "./css/App.css";
import React from "react";

import {
    BrowserRouter as Router,
    Route,
    Routes,
    Link
} from "react-router-dom"

import Home from "./Home";
import Register from "./Register";
import Logout from "./Logout";
import Chat from "./Chat";

import Login from "./Login";
import Profile from "./Profile";
import { RequireToken } from "./Auth";

export const URL = `${process.env.REACT_APP_URL}/api`
export const URL_MEDIA = process.env.REACT_APP_URL_MEDIA
export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {

        }
    }

    render() {
        return (
            <Router>
                <div className="App-header">
                    <nav id="menu">
                        <ul className="App-link">
                            <li>
                                <Link to="/">Home</Link>
                            </li>
                            <li>
                                <Link to="/register">Register</Link>
                            </li>
                            <li>
                                <Link to="/login">LogIn</Link>
                            </li>
                            <li>
                                <Link to="logout">LogOut</Link>
                            </li>
                            <li>
                                <Link to="chat">Chat</Link>
                            </li>
                            <li>
                                <Link to="profile">Profile</Link>
                            </li>
                        </ul>
                    </nav>

                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/register" element={<Register />} />
                        <Route path="/login" element={<Login />} />
                        <Route path="/logout" element={<Logout />} />
                        <Route path="/chat"
                               element={<RequireToken>
                                          <Chat />
                                        </RequireToken>} />
                        <Route path="/profile"
                               element={<RequireToken>
                                          <Profile />
                                        </RequireToken>}/>
                    </Routes>
                </div>
            </Router>
        )
    }
}
