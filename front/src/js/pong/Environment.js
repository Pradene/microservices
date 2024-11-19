import * as THREE from 'three'
import { Pong } from './Pong.js'

export class Environment {
    constructor() {

        this.game = Pong.get()

        this.scene = this.game.scene

        this.setLight()
    }

    setLight() {
        this._dLight = new THREE.DirectionalLight(0xFFFFFF, 3)
        this._dLight.position.set(0, 4, 6)
		
        this._sLight = new THREE.DirectionalLight(0xFFFFFF, 1.1)
        this._sLight.position.set(3, -2, -3)
        
        this._aLight = new THREE.AmbientLight(0xFFFFFF, 0.6)

        this.scene.add(
            this._aLight,
            this._dLight,
            this._sLight
        )
    }
}