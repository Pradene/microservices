import { Session } from "../utils/Session.js"
import { getCookie } from "../utils/utils.js"
import { WSManager } from "../utils/WebSocketManager.js"

export function connectFriendsSocket() {
    const url = "wss://" + location.hostname + ":" + location.port + "/ws/friends/"
    
    const token = getCookie('access_token')
    if (!token) {
        console.error('error: Token not defined for connecting to friend consumer')
        return
    }

    const socket = new WebSocket(url, token)
    if (!socket) return

    WSManager.add('friends', socket)

    socket.onopen = () => {
        WSManager.send('friends', {
            'type': 'hello',
            'user_id': Session.getUserID()
        })
    }

	socket.onmessage = (e) => {
        const event = new CustomEvent('friendsEvent', {
            detail: e
		})
		
		window.dispatchEvent(event)
	}

    socket.onerror = (e) => {
        console.log('error:', e)
    }

    socket.onclose = (e) => {
        console.log('close:', e)
    }

    return socket
}