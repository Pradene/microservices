import * as THREE from "three"
import { BALL_RADIUS, THREE_RATIO } from "./Defines.js"
import { Pong } from "./Pong.js"

export class Ball {
    constructor() {
        
        this.game = Pong.get()

        this.scene = this.game.scene

        this.setInstance()
    }

    setInstance() {
        const material = new THREE.MeshPhongMaterial({color: 0xE54B4B})
        
        const radius = BALL_RADIUS
        const geometry = new THREE.SphereGeometry(radius, 30, 30)

        this.instance = new THREE.Mesh(geometry, material)

        this.scene.add(this.instance)
    }

    remove() {
        this.scene.remove(this.instance)
        this.instance.material.dispose()
        this.instance.geometry.dispose()
    }

    setPosition(x, y) {
        const vec = new THREE.Vector3(0, 0, 0)
        vec.x = y / THREE_RATIO
        vec.y = 0
        vec.z = x / THREE_RATIO
        
        if (!this.instance.position.equals(vec))
            this.createParticles()
        
        this.instance.position.copy(vec)
    }

    createParticles() {
        const radius = BALL_RADIUS

        const numParticles = 24 // Number of particles in the cloud
        
        const particles = new THREE.BufferGeometry()
        const positions = new Float32Array(numParticles * 3) // Position array
        
        // Initialize particle positions and colors
        for (let i = 0; i < numParticles; i++) {
            // Randomize initial positions slightly around the origin
            const theta = Math.random() * 2 * Math.PI; // Angle around the Y-axis
            const phi = Math.acos(2 * Math.random() - 1); // Angle from the Y-axis
            const r = Math.random() * radius; // Random distance from the center within radius

            // Convert spherical coordinates to Cartesian coordinates
            positions[i * 3] = this.instance.position.x + r * Math.sin(phi) * Math.cos(theta); // x
            positions[i * 3 + 1] = this.instance.position.y + r * Math.sin(phi) * Math.sin(theta); // y
            positions[i * 3 + 2] = this.instance.position.z + r * Math.cos(phi); // z
        }

        particles.setAttribute('position', new THREE.BufferAttribute(positions, 3))
        
        const particlesMaterial = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.02
        })

        // Créer le système de particules
        const particleSystem = new THREE.Points(particles, particlesMaterial)
        this.scene.add(particleSystem)

        setTimeout(() => {
            this.scene.remove(particleSystem)

            particles.dispose()
            particlesMaterial.dispose()
        }, 300)
    }
}
