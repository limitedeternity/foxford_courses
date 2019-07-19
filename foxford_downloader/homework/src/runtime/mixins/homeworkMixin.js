import path from "path";
import fs from "fs-extra";

import helpers from "../helpers";

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
      if (
        fs.existsSync(
          path.join(
            nw.App.startPath,
            String(this.courseId),
            String(task.lessonIdx + 1),
            `${task.id}-part1.pdf`
          )
        )
      ) {
        continue;
      }

      this.foxFrame.src = "about:blank";
      await new Promise(resolve => setTimeout(resolve, 100));

      this.foxFrame.src = `https://foxford.ru/lessons/${task.lessonId}/tasks/${task.id}`;
      await new Promise(resolve => setTimeout(resolve, 500));

      try {
        let response = await fetch(
          `https://foxford.ru/api/lessons/${task.lessonId}/tasks/${task.id}/fails`,
          {
            method: "POST",
            headers: {
              "X-CSRF-Token": helpers.getCookie(
                "csrf_token",
                this.foxFrame.contentWindow.document.cookie
              )
            }
          }
        );

        if (response.ok) {
          this.foxFrame.contentWindow.location.reload(true);
          await new Promise(resolve => setTimeout(resolve, 100));
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

      let i = 0;
      do {
        let pdf_path = path.join(
          nw.App.startPath,
          String(this.courseId),
          String(task.lessonIdx + 1),
          `${task.id}-part${i + 1}.pdf`
        );

        fs.ensureFileSync(pdf_path);

        nw.Window.get().print({
          pdf_path,
          marginsType: 1,
          landscape: true,
          mediaSize: {
            name: "Responsive",
            width_microns: this.foxFrame.contentWindow.screen.width * 263.6,
            height_microns: this.foxFrame.contentWindow.screen.height * 263.6,
            custom_display_name: "Screen",
            is_default: true
          },
          headerFooterEnabled: false,
          shouldPrintBackgrounds: true
        });

        if (this.foxFrame.contentWindow.document.body
          .scrollHeight - i * this.foxFrame.contentWindow.screen.height >= this.foxFrame.contentWindow.screen.height) {
          this.foxFrame.contentWindow.scrollBy(0, this.foxFrame.contentWindow.screen.height);
        } else {
          this.foxFrame.contentWindow.scrollTo(0, this.foxFrame.contentWindow.document.body.scrollHeight);
        }

      } while (this.foxFrame.contentWindow.document.body
        .scrollHeight - ++i * this.foxFrame.contentWindow.screen.height > 0);
    }
  }
}

export default HomeworkMixin;
