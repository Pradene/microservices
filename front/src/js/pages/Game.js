import { TemplateComponent } from "../utils/TemplateComponent"
import { Pong } from "../pong/Pong"
import { WSManager } from "../utils/WebSocketManager"

export class Game extends TemplateComponent {
    constructor() {
        super()

        this.game = undefined
    }

    async unmount() {
        if (this.game)
            this.game.end()
        
        WSManager.remove('game')
    }

    async componentDidMount() {
        const id = this.getGameID()
        this.game = new Pong('remote', id)
    }

    getGameID() {
        return location.pathname.split("/")[2]
    }
}