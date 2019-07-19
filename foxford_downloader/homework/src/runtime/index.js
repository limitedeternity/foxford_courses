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

    await new Promise(resolve => setTimeout(resolve, 1000));
  }
}

class FoxfordRetriever extends mix(FoxfordRetrieverBase).with(...mixins) { }

export default FoxfordRetriever;
