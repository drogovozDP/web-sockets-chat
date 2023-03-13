import './css/App.css';
import React from 'react';


export default class Chat extends React.Component {
  state = {data: "", count: 0}

  componentDidMount() {
    const ws = new WebSocket('ws://localhost:8000/chat/1/ws')
    ws.onmessage = (ev) => {
        var messages = document.getElementById('messages')
        var message = document.createElement('li')
        var content = document.createTextNode(ev.data)
        message.appendChild(content)
        messages.appendChild(message)
    };

    this.setState({
      ws: ws,
    })
  }

  componentWillUnmount() {
    const {ws, interval} = this.state;
    ws.close()
    clearInterval(interval)
  }

  sendMessage = (ev) => {
        var input = document.getElementById("messageText")
        this.state.ws.send(input.value)
        input.value = ''
        ev.preventDefault()
    }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <h2>
            WebSocket Example
          </h2>
          <div>
              <form action="" onSubmit={this.sendMessage}>
                  <input type="text" id="messageText" autoComplete="off"/>
                  <button>Send</button>
              </form>
              <ul id='messages'>
              </ul>
          </div>
        </header>
      </div>
    )
  }
}
