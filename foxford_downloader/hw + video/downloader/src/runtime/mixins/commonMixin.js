class CommonMixin {
  constructor() {
    this.lessonList = [];
  }

  async createLessonList() {
    let json = await fetch(
      `https://foxford.ru/api/courses/${this.courseId}/lessons`
    ).then(r => r.json());

    let cursorAfter = json.cursors.after;
    let cursorBefore = json.cursors.before;

    this.lessonList = [...json.lessons];

    while (cursorBefore) {
      json = await fetch(
        `https://foxford.ru/api/courses/${
          this.courseId
        }/lessons?before=${cursorBefore}`
      ).then(r => r.json());

      this.lessonList = [...json.lessons, ...this.lessonList];
      cursorBefore = json.cursors.before;
    }

    while (cursorAfter) {
      json = await fetch(
        `https://foxford.ru/api/courses/${
          this.courseId
        }/lessons?after=${cursorAfter}`
      ).then(r => r.json());

      this.lessonList = [...this.lessonList, ...json.lessons];
      cursorAfter = json.cursors.after;
    }

    this.lessonList = this.lessonList.filter(
      lesson => lesson["timeline_view_state"] === "past" && !lesson["is_locked"]
    );
  }
}

export default CommonMixin;
