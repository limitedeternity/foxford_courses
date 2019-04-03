import React, { Component } from "react";

import { Terminal } from "xterm";
import * as fullscreen from "xterm/lib/addons/fullscreen/fullscreen";

import "xterm/dist/xterm.css";
import "xterm/lib/addons/fullscreen/fullscreen.css";

class XTerm extends Component {
  constructor(args) {
    super(args);

    Terminal.applyAddon(fullscreen);
    window.xterm = new Terminal();

    window.xterm.setOption("fontSize", 15);
    setInterval(() => window.xterm.clear(), 3000);
  }

  render() {
    return <div id="terminal" />;
  }
}

export default XTerm;
