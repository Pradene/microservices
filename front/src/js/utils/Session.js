import jwt from "jsonwebtoken"
import { getCookie } from './utils.js'

export class Session {
    static id = null

    static getUserID() {
        return Session.id
    }

    static setUserID() {
        try {
            const token = getCookie('access_token')
            if (!token)
                return

            const decoded = jwt.decode(token)
            Session.id = decoded.user_id

        } catch (e) {
            console.log('error:', e)
        }
    }

    static removeUserID() {
        Session.id = null
    }
}