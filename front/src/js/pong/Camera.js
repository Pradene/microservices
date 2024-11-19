import * as THREE from 'three'
import { Pong } from './Pong'

export class ThreeCamera {
    constructor() {

        this.game = Pong.get()

        this.sizes = this.game.sizes
        this.scene = this.game.scene
        this.canvas = this.game.canvas

        this.setInstance()
    }

    setInstance() {
        const fov = 60
        const aspect = this.sizes.width / this.sizes.height
        const near = 0.1
        const far = 100
        
        this.instance = new THREE.PerspectiveCamera(
            fov,
            aspect,
            near,
            far
        )
        
        this.instance.position.set(0, 4, 10)
        this.instance.lookAt(0, 0, 0)
        
        this.scene.add(this.instance)
    }

    // position is a THREE.Vector3
    setPosition(position) {
        this.instance.position.copy(position)
        this.instance.lookAt(0, 0, 0)
    }
    
    resize() {
        this.instance.aspect = this.sizes.width / this.sizes.height
        this.instance.updateProjectionMatrix()
    }

    update() {

    }
}