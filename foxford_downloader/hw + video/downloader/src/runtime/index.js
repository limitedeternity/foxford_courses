import mixObj from "./mixins";

const { mix, mixins } = mixObj;

class FoxfordRetrieverBase {
  constructor({ courseId }) {
    this.courseId = courseId;
    this.foxFrame = window.top.document.getElementById("foxFrame");
    this.infoEl = window.top.document.getElementById("infoEl");
  }

  async run() {
    this.foxFrame.style.display = "none";
    this.infoEl.style.display = "block";

    await this.createLessonList();
    await this.createHomeworkList();

    this.foxFrame.style.display = "block";
    this.infoEl.style.display = "none";

    await this.retrieveHomework();

    this.foxFrame.style.display = "none";
    this.infoEl.style.display = "block";

    await this.createVideoList();
    await this.createDownloadTasksList();

    this.foxFrame.src = "about:blank";
    this.foxFrame.style.display = "none";
    this.infoEl.style.display = "none";

    window.xterm.open(window.top.document.getElementById("terminal"));
    window.xterm.toggleFullScreen();

    await this.runDownloadTasks();
  }
}

class FoxfordRetriever extends mix(FoxfordRetrieverBase).with(...mixins) {}

export default FoxfordRetriever;
