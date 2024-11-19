import { TemplateComponent } from "../utils/TemplateComponent"
import { Pong } from "../pong/Pong"
import { WSManager } from "../utils/WebSocketManager"

export class Game extends TemplateComponent {
    constructor() {
        super()

        this.game = undefined
    }

    async unmount() {
        WSManager.remove('game')

        if (this.game)
            this.game.end()
    }

    async componentDidMount() {
        const id = this.getGameID()
        this.game = new Pong(id)
    }

    getGameID() {
        return location.pathname.split("/")[2]
    }
}