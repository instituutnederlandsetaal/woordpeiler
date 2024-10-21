const express = require('express');
const app = express();
const port = 8080;
const staticFileMiddleware = express.static('dist')
app.use(staticFileMiddleware)
app.use('/', staticFileMiddleware)
app.listen(port, () => {
    console.log(`App listening at http://localhost:${port}`)
})