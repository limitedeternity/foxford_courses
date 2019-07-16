import CommonMixin from "./commonMixin";
import HomeworkMixin from "./homeworkMixin";

const mix = baseClass => {
  return {
    with: (...mixins) => {
      class base extends baseClass {
        constructor(...args) {
          super(...args);

          mixins.forEach(mixin => {
            copyProps(this, new mixin());
          });
        }
      }

      let copyProps = (target, source) => {
        Object.getOwnPropertyNames(source)
          .concat(Object.getOwnPropertySymbols(source))
          .forEach(prop => {
            if (
              !prop.match(
                /^(?:constructor|prototype|arguments|caller|name|bind|call|apply|toString|length)$/
              )
            )
              Object.defineProperty(
                target,
                prop,
                Object.getOwnPropertyDescriptor(source, prop)
              );
          });
      };

      mixins.forEach(mixin => {
        copyProps(base.prototype, mixin.prototype);
        copyProps(base, mixin);
      });

      return base;
    }
  };
};

const mixins = [CommonMixin, HomeworkMixin];

export default { mix, mixins };
