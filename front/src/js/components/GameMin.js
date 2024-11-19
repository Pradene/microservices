import { Session } from "../utils/Session"

class GameMin extends HTMLElement {
    constructor() {
        super()
    }

    async connectedCallback() {
        if (this.classList.contains('tournament')) {
            await this.tournamentCallback()
            return
        }

        const userID = Session.getUserID()

        const gameid = this.getAttribute('gameid')
        const data = await (await fetch(`/api/games/gameinfo/${gameid}`)).json()

        const userid = data.user1.id == userID ? data.user1.id : data.user2.id
        const opponentid = data.user1.id == userID ? data.user2.id : data.user1.id
        const user_score = userid == data.user1.id ? data.user1_score : data.user2_score
        const opponent_score = userid == data.user1.id ? data.user2_score : data.user1_score

        this.addEventListener('click', (event) => {
            document.location = "/game/" + data.id
        })

        const player = document.createElement('user-profile')
        player.setAttribute('playerid', userid)

        const opponent = document.createElement('user-profile')
        opponent.setAttribute('playerid', opponentid)
        opponent.classList.add('end')

        const score = document.createElement('div')
        score.textContent = `${user_score} vs ${opponent_score}`
        // playerImgContainer.appendChild(playerImg)
        // player.appendChild(playerImgContainer)

        // player.appendChild(playerUsername)
        this.appendChild(player)
        this.appendChild(score)
        this.appendChild(opponent)
    }

    async tournamentCallback() {
        const userID = Session.getUserID()

        const tournamentid = this.getAttribute('gameid')
        const data = await (await fetch(`/api/games/tournamentinfo/${tournamentid}`)).json()

        const player = document.createElement('user-profile')
        player.setAttribute('playerid', userID)

        const won = userID == data.winner.id
        const result = document.createElement('p')
        result.textContent = won ? 'You won' : 'You lost'

        this.appendChild(player)
        this.appendChild(result)

        this.addEventListener('click', (event) => {
            document.location = "/tournament/" + data.id
        })
    }
}

customElements.define('game-min', GameMin)