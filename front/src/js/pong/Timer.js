import * as THREE from 'three'
import { FontLoader } from 'three/examples/jsm/loaders/FontLoader.js'
import { TextGeometry } from 'three/examples/jsm/geometries/TextGeometry.js'
import { Pong } from './Pong'

export class Timer {
    constructor() {

        this.game = Pong.get()

        this.scene = this.game.scene
        this.camera = this.game.camera.instance

        this.font = null
        this.loadFont()

        this.instance = null
    }

    loadFont () {
        const loader = new FontLoader()
        loader.load("/src/fonts/Epilogue_Bold.json",
            (f) => {
                this.font = f
            }
        )
    }

    create(time) {
        this.remove()

        const material = new THREE.MeshPhongMaterial({color: 0xDAFFFF})
        
        
        // Create geometry
        const geometry = new TextGeometry(time.toString(), {
            font: this.font,
            size: 0.5,
            height: 0.1,
            depth: 0.1,
            curveSegments: 12,
            bevelEnabled: true,
            bevelThickness: 0.02,
            bevelSize: 0.05,
            bevelOffset: 0,
            bevelSegments: 5
        })

        // Center the geometry
        geometry.computeBoundingBox()
        const boundingBox = geometry.boundingBox
        const center = new THREE.Vector3()
        boundingBox.getCenter(center)
        geometry.translate(-center.x, -center.y, -center.z)
        
        this.instance = new THREE.Mesh(geometry, material)

        const direction = new THREE.Vector3()
        this.camera.getWorldDirection(direction)
        const distance = 2
        this.instance.position.copy(this.camera.position).add(direction.normalize().multiplyScalar(distance))
        
        this.instance.rotation.copy(this.camera.rotation)

        this.scene.add(this.instance)

        // this.animate()

        setTimeout(() => {
            this.remove()
        }, 900)
    }

    remove() {
        if (this.instance) {
            this.scene.remove(this.instance)
            this.instance.geometry.dispose()
            this.instance.material.dispose()
            this.instance = null
        }
    }

    animate() {
        setTimeout(() => {
            let startTime = null
            const originalScale = this.instance.scale.clone()

            const easeOutQuad = (t) => {
                return t * (2 - t) // Easing formula
            }

            const instance = this.instance
    
            const animation = (timestamp) => {
                if (!startTime) startTime = timestamp
    
                const elapsed = timestamp - startTime
    
                // Complete the rotation in 500ms (half a second)
                const rotationProgress = Math.min(elapsed / 500, 1) // progress percentage (0 to 1)
                const easedProgress = easeOutQuad(rotationProgress)

                
                if (easedProgress <= 1) {
                    instance.rotation.y = -easedProgress * Math.PI * 2 // 360° rotation
                    
                    const scale = originalScale.x * (1 - easedProgress)
                    instance.scale.set(scale, scale, scale)

                    window.requestAnimationFrame(animation)
                
                } else {
                    // Ensure it completes a full turn
                    instance.rotation.y = Math.PI * 2
                    instance.copy.scale(originalScale)
                }
            }
    
            window.requestAnimationFrame(animation)
        }, 500)
    }
}