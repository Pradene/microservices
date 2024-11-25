import { TemplateComponent } from "../utils/TemplateComponent"
import { Pong } from "../pong/Pong"
import { WSManager } from "../utils/WebSocketManager"

export class LocalGame extends TemplateComponent {
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
        console.log('creating game')
        this.game = new Pong(null)
    }
}