import { getCookie } from "../utils/utils.js"
import { WSManager } from "../utils/WebSocketManager.js"

export function connectFriendsSocket() {
	
	const token = getCookie('access_token')
	if (!token) {
		console.error('error: Token not defined for connecting to friend consumer')
		return
	}

	const url = "wss://" + location.hostname + ":" + location.port + "/ws/friends/" + "?token=" + token

 	const socket = new WebSocket(url)
	if (!socket) return

	WSManager.add('friends', socket)

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