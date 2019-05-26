import path from "path";
import glob from "glob";
import child_process from "child_process";
import waitPort from "wait-port";

import helpers from "../helpers";

class VideoMixin {
  constructor() {
    this.videoList = [];
    this.downloadTasks = [];
  }

  async createVideoList() {
    for (let lesson of this.lessonList) {
      let id = lesson.id;

      let json = await fetch(
        `https://foxford.ru/api/courses/${this.courseId}/lessons/${id}`
      ).then(r => r.json());

      if (json.webinar_status !== "video_available") {
        continue;
      }

      let webinarId = json.webinar_id;

      let webinarSource = await fetch(
        `https://foxford.ru/groups/${webinarId}`
      ).then(r => r.text());

      let webinarDOM = new DOMParser().parseFromString(
        webinarSource,
        "text/html"
      );

      let erlyFrame = webinarDOM.querySelector("div.full_screen > iframe");

      this.foxFrame.contentWindow.location.href = erlyFrame.src;

      await helpers.waitFor(() =>
        this.foxFrame.contentWindow.document.querySelector("video")
      );

      let videoLink;

      try {
        let videoEl = this.foxFrame.contentWindow.document.querySelector(
          "#integros_player > div > div > video"
        );

        if (videoEl) {
          videoLink = videoEl.dataset.originalSrc;
        } else {
          throw new Error("Next player type");
        }
      } catch (e) {
        let videoEl = this.foxFrame.contentWindow.document.querySelector(
          "video.video-react-video > source"
        );

        if (videoEl) {
          videoLink = videoEl.src;
        } else {
          throw new Error("Unknown player type");
        }
      }

      this.videoList.push({
        url: videoLink,
        lessonId: id,
        fname: webinarId
      });

      this.foxFrame.contentWindow.location.href = "about:blank";
    }
  }

  async createDownloadTasksList() {
    for (let video of this.videoList) {
      this.downloadTasks.push({
        title: `${video.lessonId}`,
        task: `
        () => {
          return new Observable(async taskObserver => {
            let skipFilePath = path.join(
              cwd,
              "output",
              "${this.courseId}",
              "${video.lessonId}",
              "${video.fname}.skip"
            );

            if (fs.existsSync(skipFilePath)) {
              taskObserver.complete();
              return Promise.resolve();
            }

            let mp4FilePath = path.join(
              cwd,
              "output",
              "${this.courseId}",
              "${video.lessonId}",
              "${video.fname}.mp4"
            );

            fs.ensureFileSync(mp4FilePath);

            await new Promise((resolve, reject) => {
              let command = ffmpeg()
                .input("${video.url}")
                .inputOptions(["-protocol_whitelist", "file,http,https,tcp,tls"])
                .outputOptions(["-bsf:a", "aac_adtstoasc", "-preset", "superfast"])
                .audioCodec("copy")
                .videoCodec("copy")
                .save(mp4FilePath);

              command.on("start", () => {
                taskObserver.next("${video.lessonId}: N/A [0 kbps]");
              });

              command.on("progress", progress =>
                taskObserver.next(
                  \`${
                    video.lessonId
                  }: \${progress.timemark} [\${progress.currentKbps} kbps]\`
                )
              );

              command.on("error", err => {
                taskObserver.complete();
                reject(err);
              });

              command.on("end", () => {
                fs.ensureFileSync(skipFilePath);
                taskObserver.complete();
                resolve();
              });
            });
          });
        }`
      });
    }
  }

  async runDownloadTasks() {
    await new Promise(async resolve => {
      let taskServer = glob.sync(
        path.join(nw.App.startPath, "task-server*")
      )[0];

      let downloaderSlave = child_process.spawn(taskServer);

      downloaderSlave.on("exit", resolve);
      [downloaderSlave.stdout, downloaderSlave.stderr].forEach(ioStream => {
        ioStream.on("data", data => {
          window.xterm.writeln(data.toString());
        });
      });

      await waitPort({ host: "localhost", port: 3001, output: "silent" });
      await fetch("http://localhost:3001/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(this.downloadTasks)
      });
    });
  }
}

export default VideoMixin;
