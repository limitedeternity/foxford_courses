const path = require("path");
const fs = require("fs-extra");
const Observable = require("zen-observable");
const VerboseRenderer = require("listr-verbose-renderer");
const Listr = require("listr");
const ffbinaries = require("ffbinaries");
const ffmpeg = require("fluent-ffmpeg");

const cwd = process.pkg ? path.dirname(process.argv[0]) : __dirname;

function processTasks(data) {
  return new Listr(
    [
      {
        title: "Downloading ffmpeg",
        task: async () => {
          return new Observable(async taskObserver => {
            await new Promise(resolve => {
              ffbinaries.downloadBinaries(
                ["ffmpeg"],
                {
                  destination: cwd,
                  force: false,
                  tickerFn: tickData => taskObserver.next(tickData.progress)
                },
                resolve
              );
            });

            taskObserver.complete();
          });
        }
      },
      {
        title: "Setting up ffmpeg",
        task: () => {
          let locatedFf = ffbinaries.locateBinariesSync(["ffmpeg"], {
            paths: [cwd],
            ensureExecutable: true
          });

          ffmpeg.setFfmpegPath(locatedFf.ffmpeg.path);
        }
      },
      {
        title: "Downloading",
        task: () => {
          let downloadTasks = data.map(t => {
            let taskObject = t;
            taskObject.task = eval(taskObject.task);

            return taskObject;
          });

          return new Listr(downloadTasks, { concurrent: 5 });
        }
      },
      {
        title: "Finishing",
        task: () => Promise.resolve()
      }
    ],
    {
      renderer: VerboseRenderer
    }
  ).run();
}

module.exports = processTasks;
