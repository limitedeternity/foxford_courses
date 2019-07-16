const helpers = {
  waitFor(condition) {
    return new Promise(async resolve => {
      let returnedResult;

      while (!returnedResult) {
        try {
          returnedResult = condition();
        } catch (e) {
          returnedResult = null;
        }

        if (!returnedResult) {
          await new Promise(resolve => setTimeout(resolve, 500));
        }
      }

      resolve(returnedResult);
    });
  },

  getCookie(cookiename, cookie) {
    let cookiestring = RegExp("" + cookiename + "[^;]+").exec(cookie);

    return decodeURIComponent(
      !!cookiestring ? cookiestring.toString().replace(/^[^=]+./, "") : ""
    );
  }
};

export default helpers;
