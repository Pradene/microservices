import { getURL, apiRequest, truncateString } from '../utils/utils.js'
import { TemplateComponent } from '../utils/TemplateComponent.js'
import { WSManager } from '../utils/WebSocketManager.js'

export class Chat extends TemplateComponent {
    constructor() {
        super()

        this.handleSearchListener = () => this.handleSearch()
        this.WebSocketMessageListener = (e) => this.WebSocketMessage(e.detail)
    }

    async unmount() {
        const input = this.getRef('input')
        input.removeEventListener('keyup', this.handleSearchListener)
        
        window.removeEventListener('chatEvent', this.WebSocketMessageListener)
    }

    async componentDidMount() {
        await this.getRooms()

        const input = this.getRef('input')
        input.addEventListener('keyup', this.handleSearchListener)

        window.addEventListener('chatEvent', this.WebSocketMessageListener)
    }

    async getRooms() {
        try {
            const url = getURL('api/chat/rooms/')
            const data = await apiRequest(url)

            console.log(data)
            const rooms = data.rooms

            const container = this.getRef('rooms')
            rooms.forEach(async (room) => {
                const element = this.displayRoom(room)
                container.appendChild(element)
            })
            
        } catch (error) {
            console.log(error)
        }
    }

    async handleSearch() {
        const value = this.getRef('input').value
        const roomList = this.getRef('rooms')
        const rooms = roomList.children

        for (let room of rooms) {
            const name = room.querySelector('.name').textContent
            if (value && !name.includes(value)) {
                room.classList.add('hidden')
            } else {
                room.classList.remove('hidden')
            }
        }
    }

    WebSocketMessage(event) {
        const data = JSON.parse(event.data)

        if (data.type === 'message') {
            const chatRooms = this.getRef('rooms')

            const chatRoom = chatRooms.querySelector(`[data-room-id='${data.room_id}']`)

            const chatRoomMessage = chatRoom.querySelector('.message')
            chatRoomMessage.textContent = truncateString(data.content, 48)

            // Modify thhe position of the room
            // to become the first element of the list
            chatRooms.insertBefore(chatRoom, chatRooms.firstChild)
        }
    }

    displayRoom(room) {
        const element = document.createElement('li')
        element.className = 'room'
        element.dataset.roomId = room.id

        const link = document.createElement('a')
        link.className = 'link'
        link.href = `/chat/${room.id}/`
        link.dataset.link = ''

        const infoContainer = document.createElement('div')
        infoContainer.className = 'info'

        const name = document.createElement('span')
        name.className = 'name'
        name.textContent = room.name

        const message = document.createElement('span')
        message.className = 'message'
        if (room.message) {
            message.textContent = room.message.content
        } else {
            message.textContent = "Send a message..."
        }

        element.appendChild(link)
        link.appendChild(infoContainer)
        infoContainer.appendChild(name)
        infoContainer.appendChild(message)

        return element
    }
}
