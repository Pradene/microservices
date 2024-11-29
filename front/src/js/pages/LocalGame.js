import { TemplateComponent } from "../utils/TemplateComponent"
import { Pong } from "../pong/Pong"
import { WSManager } from "../utils/WebSocketManager"

export class LocalGame extends TemplateComponent {
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
        console.log('creating game')
        this.game = new Pong('local', null)
    }
}