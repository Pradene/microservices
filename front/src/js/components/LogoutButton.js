import { Router } from "../utils/Router.js"
import { getURL, apiRequest } from "../utils/utils.js"
import { WSManager } from "../utils/WebSocketManager.js"

class LogoutButton extends HTMLElement {
    constructor() {
        super()

        this._button = null
    }

    connectedCallback() {
        this._button = document.createElement("button")
        this._button.textContent = "Disconnect"
        this._button.className = "button"

        this._button.addEventListener("click", async () => {
            await this.handleClick()
        })

        this.appendChild(this._button)
    }

    async handleClick() {
        try {
            const url = getURL("api/auth/logout/")

            const data = await apiRequest(url, {
                method: "POST"
            })

            WSManager.removeAll()
            
            const router = Router.get()
            await router.navigate("/login/")

        } catch (error) {
            console.log(error)
        }
    }
}

customElements.define("logout-button", LogoutButton)
