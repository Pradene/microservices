import { WSManager } from "../utils/WebSocketManager"
import { getCookie } from "../utils/utils.js"

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
	}

	socket.onerror = (e) => {
		console.log('error:', e)
	}

	socket.onclose = (e) => {
		console.log('close:', e)
	}

	return socket
}