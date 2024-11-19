import * as THREE from 'three'

import { Pong } from './Pong.js'

export class Stadium {
    constructor() {
        this.game = Pong.get()

        this.scene = this.game.scene

        this.setInstance()
    }

    setInstance() {
        const geometry = new THREE.RingGeometry(10, 15, 32)
        const material = new THREE.MeshStandardMaterial({ color: 0xA3BAC3 })
        this.instance = new THREE.Mesh(geometry, material)
        this.instance.rotation.x = -Math.PI / 2 // Rotate to face upwards

        this.scene.add(this.instance)
    }

    remove() {
        this.scene.remove(this.instance)
        this.instance.material.dispose()
        this.instance.geometry.dispose()
    }
}