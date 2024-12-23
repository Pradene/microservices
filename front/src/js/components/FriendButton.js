import { WSManager } from '../utils/WebSocketManager.js'

class FriendButton extends HTMLElement {
    constructor() {
        super()

        this._button = document.createElement('button')
        this._status = null
        this._id = null
    }

    set status(newStatus) {
        console.log('new status', newStatus)
        this._status = newStatus
        this.updateButtonLabel()
    }

    get status() {
        return this._status
    }

    get id() {
        return this._id
    }
    
    set id(newId) {
        this._id = newId
    }

    updateButtonLabel() {
        switch (this.status) {
            case 'accepted':
                this._button.textContent = 'Remove friend'
                break
            case 'sent':
                this._button.textContent = 'Cancel'
                break
            case 'pending':
                this._button.textContent = 'Accept'
                break
            case 'none':
            default:
                this._button.textContent = 'Add friend'
                break
        }
    }

    connectedCallback() {
        this._button.className = 'button'

        this._button.addEventListener('click', () => {
            this.handleClick()
        })

        window.addEventListener('friendsEvent', (e) => this.handleWebsocketMessage(e.detail))

        this.appendChild(this._button)
    }

    handleClick() {
        switch (this.status) {
            case 'accepted':
                // Handle unfriending
                this.removeFriend()
                this.status = 'none'
                break
            case 'pending':
                // Handle accepting the request
                this.acceptIncomingFriendRequest()
                this.status = 'friend'
                break
            case 'sent':
                // Handle canceling the request
                this.cancelFriendRequest()
                this.status = 'none'
                break
            case 'none':
                // Handle sending a new friend request
                this.sendFriendRequest()
                this.status = 'sent'
                break
            default:
                this.sendFriendRequest()
                break
        }
    }

    handleWebsocketMessage(e) {
        console.log(e)
        const message = JSON.parse(e.data)

        if (!message || !message.action) return 

        if (message.action === 'friend_request_received') {
            this.status = 'pending'
        } else if (message.action === 'friend_request_accepted') {
            this.status = 'accepted'
        } else if (message.action === 'friend_request_declined') {
            this.status = 'none'
        } else if (message.action === 'friend_request_cancelled') {
            this.status = 'none'
        } else if (message.action === 'friend_removed') {
            this.status = 'none'
        }
    }

    sendFriendRequest() {
        WSManager.send('friends', {
            'type': 'friend_request_sended',
            'user_id': this._id
        })
    }

    acceptIncomingFriendRequest() {
        WSManager.send('friends', {
            'type': 'friend_request_accepted',
            'user_id': this._id
        })
    }

    declineIncomingFriendRequest() {
        WSManager.send('friends', {
            'type': 'friend_request_declined',
            'user_id': this._id
        })
    }

    cancelFriendRequest() {
        WSManager.send('friends', {
            'type': 'friend_request_cancelled',
            'user_id': this._id
        })
    }

    removeFriend() {
        WSManager.send('friends', {
            'type': 'friend_removed',
            'user_id': this._id
        })
    }
}

customElements.define('friend-button', FriendButton)
