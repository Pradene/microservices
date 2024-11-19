import { TemplateComponent } from '../utils/TemplateComponent.js'
import { getURL, apiRequest } from '../utils/utils.js'
import { Router } from '../utils/Router.js'

export class Signup extends TemplateComponent {
    constructor() {
        super()
        
        this.handleSubmitListener = async (e) => await this.handleSubmit(e)
    }
    
    async unmount() {
        const form = this.getRef('form')
        form.removeEventListener('submit', this.handleSubmitListener)        
    }

    async componentDidMount() {
        const form = this.getRef('form')
        form.addEventListener('submit', this.handleSubmitListener)
    }

    async handleSubmit(event) {
        event.preventDefault()

		const username = document.getElementById('username')
		const email = document.getElementById('email')
		const password = document.getElementById('password')
		const passwordConfirmation = document.getElementById('passwordConfirmation')


        try {
            const url = getURL('api/auth/signup/')

            const data = await apiRequest(url, {
                method: 'POST',
                body: {
                    email: email.value,
                    username: username.value,
                    password: password.value,
                    password_confirmation: passwordConfirmation.value
                }
            })

            const router = Router.get()
            await router.navigate('/login/')

        } catch (e) {
            const data = e.data
            console.log(data)
            const errors = data.errors
            
            email.value = ''
            username.value = ''
            password.value = ''
            passwordConfirmation.value = ''

            this.displayErrors(errors)
        }
    }

    displayErrors(errors) {
		const username = document.getElementById('username')
        const email = document.getElementById('email')
		const password = document.getElementById('password')
		const passwordConfirmation = document.getElementById('passwordConfirmation')
        
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

        if (errors['username']) {
            removeHidden(username, errors['username'])
        }
        
        if (errors['email']) {
            removeHidden(email, errors['email'])  
        }
        
        if (errors['password']) {
            removeHidden(password, errors['password'])
            removeHidden(passwordConfirmation, errors['password'])
        }
    }
}
