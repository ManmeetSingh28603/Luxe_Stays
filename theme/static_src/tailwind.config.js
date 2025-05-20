module.exports = {
  content: [
    "../../templates/**/*.html",
    "../../../**/*.py",
    "../../static/**/*.js",
  ],
  theme: {
    extend: {
      keyframes: {
        "slide-fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(30px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "slide-fade-in-delay": {
          "0%": { opacity: "0", transform: "translateY(30px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        "fade-in-up": "slide-fade-in-up 1.2s ease-out forwards",
        "fade-in-up-delay": "slide-fade-in-delay 1.2s ease-out forwards 0.4s",
      },
    },
  },
  plugins: [],
};
