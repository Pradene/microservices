import { Router } from "../utils/Router.js"
import { WSManager } from "../utils/WebSocketManager.js"

function handleMessage(data) {
    if (data.type === 'game_found') {
        const id = data.id
        const url = `/game/${id}/`

        const router = Router.get()
        router.navigate(url)
    }
}

export function connectTournamentSocket(id) {
    const url = `wss://${location.hostname}:${location.port}/ws/tournament/${id}/`
    const socket = new WebSocket(url)
    if (!socket) return

    WSManager.add('tournament', socket)

    sessionStorage.setItem('tournament', id)

    socket.onopen = (e) => {
        WSManager.send('tournament', {
            'type': 'ready'
        })
    }

	socket.onmessage = (e) => {
        console.log(e)
        const data = JSON.parse(e.data)
        
        handleMessage(data)
    }

    socket.onclose = () => {
        sessionStorage.removeItem('tournament')
    }

    return socket
}

