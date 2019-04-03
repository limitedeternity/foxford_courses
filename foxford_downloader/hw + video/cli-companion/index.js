const micro = require("micro");

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

  require("./processTasks")(data).then(() => setTimeout(process.exit, 1000));
  return micro.send(res, 200, "OK");
}).listen(3001);

console.log("Listening on http://localhost:3001");
