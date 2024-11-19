import {Router} from "../utils/Router"

class UserProfile extends HTMLElement {
    constructor() {
        super()
        
        this.userid = 0
    }

    async connectedCallback() {
        const userid = this.hasAttribute('userid') ? this.getAttribute('userid') : this.getAttribute('playerid')
        const data = await (await fetch(`/api/users/${userid}/`)).json()

        const playerImgContainer = document.createElement('div')
        playerImgContainer.classList.add('profile-picture')
        const playerImg = document.createElement('img')
        playerImg.src = data.picture
        const playerUsername = document.createElement('p')
        playerUsername.textContent = data.username

        playerImgContainer.appendChild(playerImg)
        this.appendChild(playerImgContainer)
        this.appendChild(playerUsername)

        this.userid = userid
        this.addEventListener("click", async (event) => {
            event.stopPropagation()
            await Router.get().navigate(`/users/${this.userid}/`)
        })
    }
}

customElements.define('user-profile', UserProfile)