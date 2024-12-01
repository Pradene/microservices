import { TemplateComponent } from "../utils/TemplateComponent.js"
import { getURL, apiRequest, getConnectedUserID } from "../utils/utils.js"
import { Session } from "../utils/Session.js"

export class Profile extends TemplateComponent {
	constructor() {
		super()
	}

	async unmount() {}

	async componentDidMount() {
		await this.getUser()
		await this.getGames()
		await this.getStats()
	}

	async getUser() {
		try {
			const id = this.getProfileID()
			const url = getURL(`api/users/${id}/profile/`)
			
			const data = await apiRequest(url)
			const user = data.user

			console.log('user:', user)

			const picture = document.getElementById("profile-picture")
			picture.src = user.picture

			const username = document.getElementById("username")
			username.textContent = user.username
			
			const level = document.querySelector(".level #level")
			level.textContent = user.level
			
			const xp = document.querySelector(".level #exp")
			xp.textContent = user.experience
			
			const xpmax = document.querySelector(".level #expMax")
			xpmax.textContent = user.experience_required
			
			const progress = document.querySelector(".information progress")            
			progress.setAttribute("max", user.experience_required)
			progress.setAttribute("value", user.experience)
			
			const buttonContainer = document.getElementById("buttons")
			if (id == Session.getUserID()) {

				const editBtton = document.createElement("a")
				editBtton.href = `/users/${Session.getUserID()}/edit/`
				editBtton.dataset.link = ""
				editBtton.textContent = "Edit"
				editBtton.classList.add('button')
				buttonContainer.appendChild(editBtton)

				const logoutButton = document.createElement("logout-button")
				buttonContainer.appendChild(logoutButton)

			} else {
				const button = document.createElement("friend-button")
				button.status = user.status
				button.id = user.id
				buttonContainer.appendChild(button)
			}

		} catch (error) {
			console.log(error)
		}
	}

	getProfileID() {
		return location.pathname.split("/")[2]
	}

	async getGames() {
		try {
			const url = getURL("api/games/history/")
			const data = await apiRequest(url)
			
			const games = data.games
			console.log('games:', games)
			
			const container = document.getElementById("games-history")
			games.forEach((game) => {
				const element = this.displayGame(game)
				container.appendChild(element)
			})
			
		} catch (e) {
			console.log(e)
			return
		}
	}

	displayGame(game) {
		let opponent = undefined
		let player = undefined

		game.users.forEach(user => {
			if (Session.getUserID() === user.id) {
				player = user
			} else {
				opponent = user
			}
		})

		const element = document.createElement('div')
		element.classList.add('game')

		const playerContainer = document.createElement('div')
		playerContainer.setAttribute('playerid', player.id)
		playerContainer.classList.add('player')
		const playerImgContainer = document.createElement('div')
		playerImgContainer.classList.add('profile-picture')
		const playerImg = document.createElement('img')
		playerImg.src = player.picture
		const playerUsername = document.createElement('p')
		playerUsername.textContent = player.username
		
		const opponentContainer = document.createElement('div')
		opponentContainer.classList.add('player', 'end')
		const opponentImgContainer = document.createElement('div')
		opponentImgContainer.classList.add('profile-picture')
		const opponentImg = document.createElement('img')
		opponentImg.src = opponent.picture
		const opponentUsername = document.createElement('p')
		opponentUsername.textContent = opponent.username

		const score = document.createElement('div')
		score.textContent = `${player.score} vs ${opponent.score}`

		playerImgContainer.appendChild(playerImg)
		playerContainer.appendChild(playerImgContainer)
		playerContainer.appendChild(playerUsername)

		opponentContainer.appendChild(opponentUsername)
		opponentImgContainer.appendChild(opponentImg)
		opponentContainer.appendChild(opponentImgContainer)

		element.appendChild(playerContainer)
		element.appendChild(score)
		element.appendChild(opponentContainer)

		return element
	}

	displayTournament(game) {
		const element = document.createElement('div')
		element.classList.add('game', 'tournament')
		element.addEventListener('click', (event) => {
			document.location = "/tournament/" + game.id
		})

		const player = document.createElement('div')
		player.classList.add('player')
		const playerImgContainer = document.createElement('div')
		playerImgContainer.classList.add('profile-picture')
		const playerImg = document.createElement('img')
		playerImg.src = game.winner.picture
		const playerUsername = document.createElement('p')
		playerUsername.textContent = game.winner.username

		const won = document.createElement('p')
		won.textContent = game.winner.id == this.getProfileID() ? "Won" : "Lost"

		playerImgContainer.appendChild(playerImg)
		player.appendChild(playerImgContainer)
		player.appendChild(playerUsername)

		element.appendChild(player)
		element.appendChild(won)

		return element
	}

	async getStats() {
		try {
			const url = getURL("api/games/stats/")
			const data = await apiRequest(url)

			this.displayStats(data)
			
		} catch (e) {
			console.log(e)
			return
		}
	}

	displayStats(stats) {
		const games = stats.total_games
		const wins = stats.wins
		const loses = stats.loses

		let winrate = 0
		if (games !== 0) {
			winrate = wins / games
		}

		const progress = document.getElementById('winrate-wins')
		progress.style.strokeDashoffset = 198 * (1 - winrate)
		
		const winrateText = document.getElementById('winrate')
		this.animateNumber(winrateText, winrate * 100, 1000)

		const gamesText = document.getElementById('games')
		this.animateNumber(gamesText, games, 200)
		
		const winsText = document.getElementById('wins')
		this.animateNumber(winsText, wins, 200)
		
		const losesText = document.getElementById('loses')
		this.animateNumber(losesText, loses, 200)
	}

	animateNumber(element, value, time) {
		const startValue = 0
		const startTime = performance.now()

		function update() {
			const currentTime = performance.now()
			const elapsedTime =  currentTime - startTime
			const progress = Math.min(elapsedTime / time, 1)

			const currentValue = Math.floor(startValue + (value - startValue) * progress)
			element.textContent = currentValue
		
			if (progress < 1) {
				requestAnimationFrame(update)
			}
		}

		update()
	}
}
