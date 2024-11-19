import { TemplateComponent } from '../utils/TemplateComponent.js'
import { getURL, apiRequest } from '../utils/utils.js'
import { Router } from '../utils/Router.js'
import { connectChatSocket } from '../websockets/Chat.js'
import { connectFriendsSocket } from '../websockets/Friends.js'
import { Session } from '../utils/Session.js'

export class Login extends TemplateComponent {
    constructor() {
        super()
        
        this.submit42LoginRequestListener = async (e) => await this.submit42LoginRequest(e)
        this.submitLoginRequestListener = async (e) => await this.submitLoginRequest(e)
    }
    
    async unmount() {
        const form = this.getRef('form')
        form.removeEventListener('submit', this.submitLoginRequestListener)
        
        const OAuthButton = this.getRef('ft_auth')
        OAuthButton.removeEventListener('click', this.submit42LoginRequestListener)
    }

    async componentDidMount() {
        const form = this.getRef('form')
        form.addEventListener('submit', this.submitLoginRequestListener)

        const OAuthButton = this.getRef('ft_auth')
        OAuthButton.addEventListener('click', this.submit42LoginRequestListener)
    }

    async submitLoginRequest(event) {
        event.preventDefault()

        const username = document.getElementById('username')
        const password = document.getElementById('password')
        const rememberMe = document.getElementById('remember-me')
        const url = getURL('api/auth/login/')

        try {
            const data = await apiRequest(url, {
                method: 'POST',
                body: {
                    username: username.value,
                    password: password.value,
                    remember_me: rememberMe.value
                }
            })

            const router = Router.get()
            if (data['2fa_enabled']) {
                await router.navigate("/verify-otp/")

            } else {
                Session.setUserID()

                connectChatSocket()
                connectFriendsSocket()

                await router.navigate("/")
            }

        } catch (e) {
            const data = e.data
            const error = data.error

            username.value = ''
            password.value = ''

            this.displayErrors(error)
        }
    }

    async submit42LoginRequest() {
        try {
            const url = getURL('api/auth/oauth/')
            const data = await apiRequest(url)

            if (data.url) {
                window.location.href = data.url

            } else {
                throw new Error(`Couldn't redirect to external API`)
            }

        } catch (e) {
            console.log(e)
        }
    }

    displayErrors(error) {
		const username = document.getElementById('username')
		const password = document.getElementById('password')
        
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
            element.insertAdjacentElement('afterend', error)

        }

        removeHidden(username, error)
        removeHidden(password, error)
    }
}
