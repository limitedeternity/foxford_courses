### _Это - инструкция по сохранению презентаций напрямую из уроков курсов Фоксфорда._

**Способ 1**:

![image](https://user-images.githubusercontent.com/24318966/58759940-64f6bd00-853a-11e9-9fc6-07eb2efd7119.png)

![image](https://user-images.githubusercontent.com/24318966/58759948-835cb880-853a-11e9-8451-92dad1d1d3f8.png)

**Способ 2**:

На странице с видео, открыв DevTools (`Shift + Ctrl + I`) во вкладке Network нужно поймать `events.json`.

![Screenshot from 2019-06-05 15-39-43](https://user-images.githubusercontent.com/24318966/58957313-0c792700-87a9-11e9-8a4c-a3eee72453c2.png)

Копируешь ссылку на него, вставляешь в [этот фрагмент кода](https://gist.github.com/limitedeternity/e88c1a375ca8ebb97329ee758431dc0a)

Выполняешь фрагмент кода во вкладке Console в DevTools, а затем - `downloadPdfFiles(createPdfFileList(json));`.
