import { TemplateComponent } from "../utils/TemplateComponent.js"
import { getURL, apiRequest } from "../utils/utils.js"
import { Router } from '../utils/Router.js'

export class EditProfile extends TemplateComponent {
    constructor() {
        super()

        this.handleSubmitListener = async (e) => await this.handleSubmit(e)
        this.handlePictureChangeListener = (e) => this.handlePictureChange(e)
    }

    async unmount() {
        const form = document.getElementById("form")
        form.removeEventListener("submit", this.handleSubmitListener)
        
        const input = document.getElementById("file-upload")
        input.removeEventListener("change", this.handlePictureChangeListener)
    }

    async componentDidMount() {
        this.getUserInfo()

        const form = document.getElementById("form")
        form.addEventListener("submit", this.handleSubmitListener)
        
        const input = document.getElementById("file-upload")
        input.addEventListener("change", this.handlePictureChangeListener)
    }

    async getUserInfo() {
        try {
            const id = this.getProfileID()
            const url = getURL(`api/users/${id}/profile/`)

            const data = await apiRequest(url)
            const user = data.user

            const picture = document.getElementById("picture-preview")
            const username = document.getElementById("username")
            const email = document.getElementById("email")
            const is_2fa_enabled = document.getElementById("is_2fa_enabled")

            picture.src = user.picture
            username.value = user.username
            email.value = user.email
            is_2fa_enabled.checked = user.is_2fa_enabled

        } catch (e) {
            console.log(e)
            return
        }
    }

    handlePictureChange(e) {
        const picture = document.getElementById("picture-preview")
        const file = e.target.files[0]

        if (file) {
            const reader = new FileReader()
            reader.onload = function(e) {
                picture.src = e.target.result
            }
            reader.readAsDataURL(file)
        
        } else {
            picture.src = ''
        }
    }

	async handleSubmit(e) {
        e.preventDefault()

        const input = document.getElementById("file-upload")
        const username = document.getElementById("username")
        const email = document.getElementById("email")
        const is_2fa_enable = document.getElementById("is_2fa_enabled")

        try {
            const body = new FormData()

            body.append("username", username.value)
            body.append("email", email.value)
            body.append("is_2fa_enabled", is_2fa_enable.checked)

            const file = input.files[0]
            if (file)
                body.append("picture", file)
            
            const id = this.getProfileID()
            const url = getURL(`api/users/${id}/profile/`)
            
            const data = await apiRequest(url, {
                method: "POST",
                body: body
            })

            const router = Router.get()
            router.back()

        } catch (e) {
			const data = e.data
			const errors = data.errors

			this.displayErrors(errors)
        }
    }

	displayErrors(errors) {
		const username = document.getElementById('username')
        const email = document.getElementById('email')
        
        const removeHidden = (element, errorMessage) => {
            const error = document.createElement('div')
            error.className = 'form-error'
            
            const img = document.createElement('img')
            img.src = '/assets/error.svg'
            img.height = 16
            img.width = 16

            const message = document.createElement('div')
            message.textContent = errorMessage

            error.appendChild(img)
            error.appendChild(message)

			const existingError = element.nextElementSibling
			if (!existingError) {
				element.insertAdjacentElement('afterend', error)
			}

			element.classList.add('shake')

			setTimeout(() => {
				element.classList.remove('shake')
			}, 300)
        }

        if (errors['username']) {
            removeHidden(username, errors['username'])
        }
        
        if (errors['email']) {
            removeHidden(email, errors['email'])  
        }
    }

    getProfileID() {
        return location.pathname.split("/")[2]
    }
}
