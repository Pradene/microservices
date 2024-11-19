export class WSManager {
    static sockets = {}
    static pendingMessages = {}

    static add(type, socket) {
        if (this.sockets[type]) {
            console.log(`Already connected to socket type ${type}`)
            return this.sockets[type]
        }

        if (!socket) return null
        
        this.sockets[type] = socket

        return socket
    }

    static remove(type) {
        const socket = this.sockets[type]
        if (!socket) return

        delete this.sockets[type]
        socket.close()
    }

    static removeAll() {
        for (const type in this.sockets) {
            if (this.sockets[type] instanceof WebSocket) {
                this.sockets[type].close()
                console.log(`Closed socket of type: ${type}`)
            }
            delete this.sockets[type]
        }
    }

    static get(type) {
        return this.sockets[type]
    }

    static send(type, message) {
        try {
            const socket = this.sockets[type]

            if (socket && socket.readyState === WebSocket.OPEN) {
                const m = JSON.stringify(message)
                socket.send(m)

            } else if (socket) {
                this.queueMessage(type, message) // Queue the message if the socket isn't ready
            }

        } catch (error) {
            console.log(error)
        }
    }

    static queueMessage(type, message) {
        if (!this.pendingMessages[type]) {
            this.pendingMessages[type] = []
        }

        this.pendingMessages[type].push(message)
    }

    static flushPendingMessages(type) {
        const socket = this.sockets[type]
        if (socket && socket.readyState === WebSocket.OPEN) {
            const messages = this.pendingMessages[type] || []
            
            messages.forEach(message => {
                socket.send(JSON.stringify(message))
            })
            
            this.pendingMessages[type] = []
        }
    }
}
