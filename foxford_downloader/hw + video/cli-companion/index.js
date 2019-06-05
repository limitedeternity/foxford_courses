const micro = require("micro");
const port = Number(require("minimist")(process.argv.slice(2)).p);

let downloadStarted = false;
micro(async (req, res) => {
  let data = await micro.json(req);

  if (
    !Array.isArray(data) ||
    data.length < 1 ||
    data[0].constructor !== Object ||
    !data[0].hasOwnProperty("task") ||
    typeof data[0].task !== "string"
  ) {
    return micro.send(res, 422, "UNPROCESSABLE ENTITY");
  }

  if (!downloadStarted) {
    require("./processTasks")(data);
    downloadStarted = true;
    return micro.send(res, 200, "OK");
  } else {
    return micro.send(res, 410, "ALREADY STARTED");
  }
}).listen(port);

console.log(`Listening on http://localhost:${port}`);
