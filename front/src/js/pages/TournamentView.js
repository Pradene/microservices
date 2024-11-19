import {TemplateComponent} from "../utils/TemplateComponent"

export class TournamentView extends TemplateComponent {
    constructor() {
        super()
    }

    async componentDidMount() {
        const gameinfo = await (await fetch(`/api/games/tournamentinfo/${this.getGameID()}`)).json()
        if (gameinfo.exists === false)
            this.displayNotFound()

        const winner = gameinfo.winner
        const user1 = gameinfo.data[0]
        const user2 = gameinfo.data[1]

        const container = document.querySelector(".stat")

        const winnerElement = document.createElement("user-profile")
        winnerElement.setAttribute("playerid", winner.id)
        winnerElement.classList.add('winner')

        container.appendChild(winnerElement)
        gameinfo.data.forEach((game, key) => {
            const element = document.createElement("game-min")
            element.setAttribute("gameid", game.id)
            element.classList.add(`g${key + 1}`)
            container.appendChild(element)
        })
    }

    displayNotFound() {
        document.querySelector(".gameview").classList.add("not-found")
    }

    getGameID() {
        return location.pathname.split("/")[2]
    }
}