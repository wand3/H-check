const { fontFamily } = require("tailwindcss/defaultTheme");
const Unfonts = require("unplugin-fonts");

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // for setting background images 
      // backgroundImage: {
      // 	'light-pattern': "url('src/assets/darkness.webp')",
      // 	'dark-pattern': "#000000",
      // }
      colors: {
      // 7: "#8A8A8A"
          color: {
            1: "#ffc876",
            2: "#FFC876",
            3: "#d9ccae8f",
            4: "#7ADB78",
            5: "#858DFF",
            6: "#FF98E2",
            7: "#d8d2d2ed",
            8: "#aca1888f",
            9: "#e7e9ec"
          },
          stroke: {
            1: "#26242C",
            2: "#aca1888f"
          },
          n: {
            1: "#000000",
            2: "#CAC6DD",
            3: "#1a1a1aeb",
            4: "#010101bf",
            5: "#3F3A52",
            6: "#15131d",
            7: "#15131D",
            8: "#F4F2F0",
            9: "#474060",
            10: "#43435C",
            11: "#1B1B2E",
            12: "#2E2A41",
            13: "#6C7275",
          },
        },
      
      fontFamily: {
        poppins: ["Poppins", ...fontFamily.sans],
        oswald: ["Oswald", ...fontFamily.sans],
        iceberg: ["Iceberg-Regular", ...fontFamily.sans],
        electrolize: ["Electrolize", ...fontFamily.sans],

      },
      letterSpacing: {
        tagline: ".15em",
      },
        spacing: {
          0.25: "0.0625rem",
          7.5: "1.875rem",
          15: "3.75rem",
        },
        opacity: {
          15: ".15",
        },
        transitionDuration: {
          DEFAULT: "200ms",
        },
        transitionTimingFunction: {
          DEFAULT: "linear",
        },
        zIndex: {
          1: "1",
          2: "2",
          3: "3",
          4: "4",
          5: "5",
        },
        borderWidth: {
          DEFAULT: "0.0625rem",
        },
        backgroundImage: {
          "radial-gradient": "radial-gradient(var(--tw-gradient-stops))",
          "conic-gradient":
            "conic-gradient(from 225deg, #FFC876, #79FFF7, #9F53FF, #FF98E2, #FFC876)",
        },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    function ({ addUtilities }) {
      const newUtilities = {
        ".container": {
          "@apply max-w-[77.5rem] mx-auto px-2 md:px-10 lg:px-15 xl:max-w-[87.5rem]":
            {},
        },
        ".h1": {
          "@apply font-semibold text-[2.5rem] leading-[3.25rem] md:text-[2.75rem] md:leading-[3.75rem] lg:text-[3.25rem] lg:leading-[4.0625rem] xl:text-[3.75rem] xl:leading-[4.5rem]":
            {},
        },
        ".h2": {
          "@apply text-[1.75rem] leading-[2.5rem] md:text-[2rem] md:leading-[2.5rem] lg:text-[2.5rem] lg:leading-[3.5rem] xl:text-[3rem] xl:leading-tight":
            {},
        },
        ".h3": {
          "@apply text-[2rem] leading-normal md:text-[2.5rem]": {},
        },
        ".h4": {
          "@apply text-[1.5rem] md:text-[2rem] leading-normal": {},
        },
        ".h5": {
          "@apply text-2xl leading-normal": {},
        },
        ".h6": {
          "@apply font-semibold text-lg leading-8": {},
        },
      };
      addUtilities(newUtilities, ['responsive', 'hover']);
    },
    
  ]


}


