import jwt from "jsonwebtoken"

import { Session } from "./Session.js"

export function getURL(url) {
    return "https://" + location.hostname + ":" + location.port + "/" + url
}

// CSRF Tokens utils
export async function fetchCSRFToken() {
    try {
        const url = getURL('api/csrf-token/')
        const data = await apiRequest(url, {
            method: 'GET'
        })

    } catch (e) {
        return
    }
}

// CSRF Tokens utils
export function getCSRFToken() {
    return getCookie('csrftoken')
}

export function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2)
        return parts.pop().split(';').shift()
    
    return null
}

// Requests to server utils
export async function apiRequest(url, options = {}) {
    try {
        let headers = new Headers()

        const method = options.method ? options.method.toUpperCase() : 'GET'
        
        const csrfToken = getCSRFToken()
        if (csrfToken)
            headers.append("X-CSRFToken", csrfToken)

        if (options.headers) {
            Object.entries(options.headers).forEach(([key, value]) => {
                headers.append(key, value)
            })
        }

        const fetchOptions = {
            method: method,
            headers: headers,
            credentials: "include",
            ...options
        }

        if (options.body) {
            if (options.body instanceof FormData) {
                fetchOptions.body = options.body

            } else {
                fetchOptions.body = JSON.stringify(options.body)
                fetchOptions.headers.append('Content-Type', 'application/json')
            }
        }

        const response = await fetch(url, fetchOptions)
        const data = await response.json()
        console.log(data)

        if (response.ok) {
            return data

        } else {
            if (response.status == 401) {
                const refreshed = await refreshToken()
                if (refreshed) {
                    return await apiRequest(url, options)
                } else {
                    throw new Error("Couldn't refresh access token")
                }

            } else {
                const error = new Error()
                error.message = 'Error during api call'
                error.status = response.status
                error.data = data
                throw error
            }
        }

    } catch (e) {
        console.error('Api request error:', e)
        throw e
    }
}

async function refreshToken() {
    const url = getURL("api/auth/token/")
    
    try {
        const data = await apiRequest(url, {
            method: "POST"
        })

        Session.setUserID()
        return true

    } catch (e) {
        return false
    }
}

export async function checkLogin() {
    try {
        const access = getCookie("access_token")
        if (!access) {
            const value = await refreshToken()

            return value
        }

        const decoded = jwt.decode(access)
        const current = Date.now() / 1000

        
        if (decoded.exp > current) {
            Session.setUserID()
            return true

        } else {
            const value = await refreshToken()
            return value
        }

    } catch (error) {
        return false
    }
}


export function truncateString(string, maxLength) {
    if (string.length > maxLength)
        return string.substring(0, maxLength) + "..."

    return string
}
