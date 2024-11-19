export class TemplateComponent {
    // Not initialize this class, use derived class
    constructor() {
        this.container = null
    }

    getTemplateURL() {
        return "/src/js/templates/" + this.constructor.name + ".html"
    }

    getRef(name) {
        const element = document.querySelector(`[ref="${name}"]`)

        return element
    }

    render() {
        fetch(this.getTemplateURL())
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser()
                const doc = parser.parseFromString(html, "text/html")
                
                if (doc.body) {
                    const app = document.getElementById('app')
                    app.replaceChildren()
                    // Iterate over each child node and append to the current document's body
                    Array.from(doc.body.childNodes).forEach(child => {
                       app.appendChild(child.cloneNode(true))
                    })

                    return app 

                } else {
                    return Promise.reject("No content found")
                }
            })
            .then(() => {
                this.componentDidMount()
            })
            .catch(error => {console.log("Error:", error)})
    }

    componentDidMount() {}
}
