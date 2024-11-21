import { WSManager } from "../utils/WebSocketManager"
import { getCookie } from "../utils/utils.js"

export function connectChatSocket() {
	const url = "wss://" + location.hostname + ":" + location.port + "/ws/chat/"
	const token = getCookie('access_token')
	if (!token) {
		console.error('error: Token not defined for connecting to friend consumer')
		return
	}

	const socket = new WebSocket(url, token)
	if (!socket) return

	WSManager.add('chat', socket)

	socket.onmessage = (e) => {
		console.log(e)
		const event = new CustomEvent('chatEvent', {
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