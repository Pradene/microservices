import {TemplateComponent} from "../utils/TemplateComponent";

export class GameView extends TemplateComponent {
    constructor() {
        super();
    }

    async componentDidMount() {
        const gameinfo = await (await fetch(`/api/games/gameinfo/${this.getGameID()}`)).json()
        console.log(gameinfo)

        if (gameinfo.exists === false)
            this.displayNotFound()

        const winner_id = gameinfo.winner.id
        const user1_id = gameinfo.user1.id
        const user1_score = gameinfo.user1_score
        const user2_id = gameinfo.user2.id
        const user2_score = gameinfo.user2_score

        const winner_element = document.createElement('user-profile')
        winner_element.setAttribute('userid', winner_id)
        winner_element.classList.add('winner')

        const user1_element = document.createElement('user-profile')
        user1_element.setAttribute('userid', user1_id)
        user1_element.classList.add('username')

        const user2_element = document.createElement('user-profile')
        user2_element.setAttribute('userid', user2_id)
        user2_element.classList.add('username')

        //todo: add score and append elements to container
        const container = document.querySelector('.stat')
        const table_begin = document.querySelector('.table')
        const user1_score_element = document.querySelector('.p1 .score')
        const user2_score_element = document.querySelector('.p2 .score')

        container.insertBefore(winner_element, table_begin)
        document.querySelector('.p1').insertBefore(user1_element, user1_score_element)
        document.querySelector('.p2').insertBefore(user2_element, user2_score_element)
        user1_score_element.textContent = user1_score
        user2_score_element.textContent = user2_score
    }

    displayNotFound() {
        document.querySelector(".gameview").classList.add("not-found")
    }

    getGameID() {
        return location.pathname.split("/")[2]
    }
}