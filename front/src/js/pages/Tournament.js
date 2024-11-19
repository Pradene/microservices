import { TemplateComponent } from '../utils/TemplateComponent.js'
import { connectTournamentSocket } from '../websockets/Tournament.js'

export class Tournament extends TemplateComponent {
    constructor() {
        super()
    }

    unmount() {
    
    }

    async componentDidMount() {
        const id = this.getTournamentID()
        const socket = connectTournamentSocket(id)
    }

    getTournamentID() {
        return location.pathname.split('/')[2]
    }
}