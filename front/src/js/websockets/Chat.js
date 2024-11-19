import { WSManager } from "../utils/WebSocketManager"

export function connectChatSocket() {
    const url = "wss://" + location.hostname + ":" + location.port + "/ws/chat/"
    const socket = new WebSocket(url)
    if (!socket) return

    WSManager.add('chat', socket)

    socket.onmessage = (e) => {
        const event = new CustomEvent('chatEvent', {
            detail: e
        })
    
        window.dispatchEvent(event)

        console.log(event)
    }

    return socket
}