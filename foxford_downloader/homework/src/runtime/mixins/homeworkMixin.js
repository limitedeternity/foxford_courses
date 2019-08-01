/* eslint-disable no-loop-func */

import path from "path";
import fs from "fs-extra";
import Jimp from "jimp/es";
import mergeImg from "merge-img";

import helpers from "../helpers";

const sizeOf = require("image-size");

class HomeworkMixin {
  constructor() {
    this.homeworkList = [];
  }

  async createHomeworkList() {
    for (let [idx, lesson] of this.lessonList.entries()) {
      let json = await fetch(
        `https://foxford.ru/api/lessons/${lesson.id}/tasks`
      ).then(r => r.json());

      if (json) {
        json.forEach(task => {
          let modTask = task;
          modTask.lessonId = lesson.id;
          modTask.lessonIdx = idx;
          this.homeworkList.push(modTask);
        });
      }
    }
  }

  async retrieveHomework() {
    for (let task of this.homeworkList) {
      let targetPath = path.join(
        nw.App.startPath,
        String(this.courseId),
        String(task.lessonIdx + 1),
        `${task.id}.png`
      );

      if (fs.existsSync(targetPath)) {
        continue;
      }

      this.foxFrame.src = "about:blank";
      await new Promise(resolve => setTimeout(resolve, 100));

      this.foxFrame.src = `https://foxford.ru/lessons/${task.lessonId}/tasks/${task.id}`;
      await new Promise(resolve => setTimeout(resolve, 500));

      try {
        let response = await this.foxFrame.contentWindow.fetch(
          `https://foxford.ru/api/lessons/${task.lessonId}/tasks/${task.id}/fails`,
          {
            method: "POST",
            headers: {
              "X-CSRF-Token": helpers.getCookie(
                "csrf_token",
                this.foxFrame.contentWindow.document.cookie
              ),
              "X-Requested-With": "XMLHttpRequest"
            }
          }
        );

        if (response.ok) {
          this.foxFrame.contentWindow.location.reload(true);
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      } catch (e) { }

      await helpers.waitFor(() =>
        this.foxFrame.contentWindow.document.querySelector("#taskContent")
      );

      nw.Window.get().resizeTo(this.foxFrame.contentWindow.screen.width, this.foxFrame.contentWindow.screen.height);

      await new Promise(resolve => setTimeout(resolve, 100));

      await helpers.waitFor(() => this.foxFrame.contentWindow.MathJax);

      await new Promise(resolve => setTimeout(resolve, 3500));

      await new Promise(resolve => {
        this.foxFrame.contentWindow.MathJax.Hub.Register.StartupHook(
          "End",
          resolve
        );
      });

      let screenshotPaths = [];
      let i = 0;
      let offset = 0;
      let scrollHeight = Math.max(
        this.foxFrame.contentWindow.document.body.scrollHeight,
        this.foxFrame.contentWindow.document.body.offsetHeight,
        this.foxFrame.contentWindow.document.documentElement.clientHeight,
        this.foxFrame.contentWindow.document.documentElement.scrollHeight,
        this.foxFrame.contentWindow.document.documentElement.offsetHeight
      );

      while (offset < scrollHeight) {
        this.foxFrame.contentWindow.scrollTo(0, offset);
        await new Promise(resolve => setTimeout(resolve, 100));

        let screenshotPath = path.join(
          nw.App.startPath,
          String(this.courseId),
          String(task.lessonIdx + 1),
          `${task.id}-part${i++ + 1}.png`
        );

        await fs.ensureFile(screenshotPath);
        screenshotPaths.push(screenshotPath);

        let imgBuffer = await new Promise(resolve => {
          nw.Window.get().capturePage(resolve, { format: "png", datatype: "buffer" });
        });

        await fs.writeFile(screenshotPath, imgBuffer);
        offset += sizeOf(imgBuffer).height;

        if (scrollHeight - offset < 0) {
          await new Promise(resolve => {
            new Jimp(imgBuffer, function () {
              this.crop(0, offset - scrollHeight, sizeOf(imgBuffer).width, sizeOf(imgBuffer).height - (offset - scrollHeight))
                .write(screenshotPath, resolve);
            });
          });
        }
      }

      let targetImg = await mergeImg(screenshotPaths, { direction: true });
      targetImg.write(targetPath);
      screenshotPaths.forEach(async p => await fs.unlink(p));
    }
  }
}

export default HomeworkMixin;
