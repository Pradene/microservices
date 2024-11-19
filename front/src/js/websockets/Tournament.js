import { Router } from "../utils/Router.js"

function handleMessage(event) {
    const data = JSON.parse(event.data)

    if (data.type === 'game_found') {
        const id = data.game_id
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

	socket.onmessage = (event) => handleMessage(event)

    socket.onclose = () => sessionStorage.removeItem('tournament')

    return socket
}

