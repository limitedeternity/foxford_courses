import React, { Component } from "react";
import "./App.css";

import FoxfordRetriever from "./runtime";
import helpers from "./runtime/helpers";

class App extends Component {
  constructor(props) {
    super(props);

    nw.Window.get().on("close", () => {
      nw.App.quit();
    });
  }

  async componentDidMount() {
    let waitResult = await helpers.waitFor(() =>
      window.top.document
        .getElementById("foxFrame")
        .contentWindow.location.href.match(
          /^https:\/\/foxford\.ru\/courses\/(\d+)$/
        )
    );

    let fdl = new FoxfordRetriever({
      courseId: waitResult[1]
    });

    await fdl.run();
    nw.Window.get().close();
  }

  render() {
    return (
      <div>
        <iframe
          id="foxFrame"
          title="foxFrame"
          nwdisable="true"
          nwfaketop="true"
          allowFullScreen
          frameBorder="0"
          referrerPolicy="no-referrer"
          src="https://foxford.ru/user/login?redirect=/dashboard"
        />
        <h1 id="infoEl">Background processes are running. Please wait.</h1>
      </div>
    );
  }
}

export default App;
