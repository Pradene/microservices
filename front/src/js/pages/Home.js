import { TemplateComponent } from '../utils/TemplateComponent.js'
import {Router} from '../utils/Router.js'
import { WSManager } from '../utils/WebSocketManager.js'

export class Home extends TemplateComponent {
    constructor() {
        super()
    }

    async unmount() {
        WSManager.remove('matchmaking')
    }

    async componentDidMount() {
        const gameButton = document.querySelector('button.create-game')
        const tournamentButton = document.querySelector('button.create-tournament')
        const cancelButton = document.querySelector('#cancel-matchmaking')

        tournamentButton.addEventListener('click', async () => this.matchmaking('tournament'))

        gameButton.addEventListener('click', async () => this.matchmaking('game'))

        cancelButton.addEventListener('click', () => this.cancelMatchmaking())
    }

    matchmaking(type) {
        if (!type) return

        this.showLoadingScreen()

        const url = `wss://${location.hostname}:${location.port}/ws/matchmaking/${type}/`
        const socket = new WebSocket(url)
        
        socket.onmessage = async (e) => {
            await this.handleMessage(e)
        }

        WSManager.add('matchmaking', socket)
    }

    cancelMatchmaking() {
        WSManager.remove('matchmaking')
        this.removeLoadingScreen()
    }

    async handleMessage(e) {
        const data = JSON.parse(e.data)
        const router = Router.get()
        
        if (data.type == 'game_found') {
            const id = data.game_id
            await router.navigate(`/game/${id}/`)
            
        } else if (data.type === 'tournament_found') {
            const id = data.tournament_id
            await router.navigate(`/tournament/${id}/`)
        }
    }

    showLoadingScreen() {
        const loadingScreen = document.querySelector('.loading-screen')
        loadingScreen.classList.add('active')
    }

    removeLoadingScreen() {
        const loadingScreen = document.querySelector('.loading-screen')
        loadingScreen.classList.remove('active')
    }
}
