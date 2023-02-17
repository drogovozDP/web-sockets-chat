import React from "react";

import Header from "./components/Header"

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            helpText: "Help text",
            userData: "",
        }

        this.inputClick = this.inputClick.bind(this)
    }

    render() {
        return (<div className="name">
            <Header title="Шапка сайта!"/>
            <h1>{this.state.helpText}</h1>
            <h2>{this.state.userData}</h2>
            <input placeholder={this.state.helpText}
                   onChange={event => this.setState({"userData": event.target.value})}
                   onClick={this.inputClick} onMouseEnter={this.mouseOver}/>
            <p>{this.state.helpText === "Help text" ? "Yes" : "No"}</p>
        </div>)
    }

    inputClick() {
        // this.state.helpText = "Changed"
        this.setState({helpText: "Changed"})
        console.log("Click button")
    }

    mouseOver() {
        console.log("Mouse over")
    }
}

export default App