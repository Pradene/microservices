import * as THREE from 'three'
import { Pong } from './Pong'

export class ThreeRenderer {
    constructor() {

        this.game = Pong.get()

        this.scene = this.game.scene
        this.sizes = this.game.sizes
        this.camera = this.game.camera
        this.canvas = this.game.canvas

        this.instance = null

        this.setInstance()
    }

    setInstance() {
        this.instance = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true
        })

        this.instance.setSize(this.sizes.width, this.sizes.height)
        this.instance.setPixelRatio(this.sizes.pixelRatio)
    }

    update() {
        this.instance.render(this.scene, this.camera.instance)
    }

    resize() {
        this.instance.setSize(this.sizes.width, this.sizes.height)
        this.instance.setPixelRatio(this.sizes.pixelRatio)
    }
}