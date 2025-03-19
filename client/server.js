const express = require('express')
const history = require('connect-history-api-fallback')

const app = express()
const port = 8080
const staticFileMiddleware = express.static('dist')

// log access
app.use((req, res, next) => {
    console.log(`${req.method} ${req.url}`)
    next()
})

// Note!: use history should come before use static middleware. Otherwise subpages don't load.
app.use(history({ index: '/index.html' }))
app.use('/couranten', staticFileMiddleware)
app.get('/couranten/*', (req, res) => {
    res.sendFile(path.join(__dirname, 'dist', 'index.html'));
  });

app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`)
})