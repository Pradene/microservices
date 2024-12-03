import { TemplateComponent } from '../utils/TemplateComponent.js'
import { apiRequest, getURL } from '../utils/utils.js'
import { connectTournamentSocket } from '../websockets/Tournament.js'

export class Tournament extends TemplateComponent {
    constructor() {
        super()
    }

    unmount() {
    
    }

    async componentDidMount() {
        await this.getTournamentInfo()

        const id = this.getTournamentID()
        const socket = connectTournamentSocket(id)
    }

    async getTournamentInfo() {
        try {
            const url = getURL(`api/tournaments/${this.getTournamentID()}`)
            const data = await apiRequest(url)
            const tournament = data.tournament
            
            this.displayTournament(tournament)
            
        } catch (e) {
            return
        }
    }
    
    displayTournament(tournament) {
        console.log(tournament.users)
        console.log(tournament.games)

        const games = tournament.games
        const users = tournament.users

        const usersMap = users.reduce((map, user) => {
            map[user.id] = user
            return map
        }, {})

        const gamesList = document.getElementById('games-list')
        games.forEach((game) => {
            const element = document.createElement('div')
            element.classList.add('game')

            game.users = game.user_ids.map((user_id) => usersMap[user_id])
            game.users.forEach((user) => {
                const gameUser = document.createElement('div')
                gameUser.classList.add('user')

                const gameUserPicture = document.createElement('img')
                gameUserPicture.classList.add('picture')
                gameUserPicture.src = user.picture
                const gameUserUsername = document.createElement('div')
                gameUserUsername.classList.add('username')
                gameUserUsername.textContent = user.username
                
                gameUser.appendChild(gameUserPicture)
                gameUser.appendChild(gameUserUsername)
                element.appendChild(gameUser)
            })

            gamesList.appendChild(element)
        })
        
        const usersList = document.getElementById('users-list')
        users.forEach((user) => {
            const tournamentUser = document.createElement('div')
            tournamentUser.classList.add('user')

            const gameUserPicture = document.createElement('img')
            gameUserPicture.classList.add('picture')
            gameUserPicture.src = user.picture
            const gameUserUsername = document.createElement('div')
            gameUserUsername.classList.add('username')
            gameUserUsername.textContent = user.username

            tournamentUser.appendChild(gameUserPicture)
            tournamentUser.appendChild(gameUserUsername)
            usersList.appendChild(tournamentUser)
        })
        
    }

    getTournamentID() {
        return location.pathname.split('/')[2]
    }
}