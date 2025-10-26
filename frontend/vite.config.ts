import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "@tailwindcss/vite";
import path from 'path';
import { fileURLToPath } from 'url'; // Required for path resolution

// Get the absolute path to your node_modules directory
const NODE_MODULES_PATH = fileURLToPath(new URL('node_modules', import.meta.url));

export default defineConfig({
  plugins: [
    tailwindcss(),
    react()
  ],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
      // map the repo alias to your local components folder
      // "@repo/shadcn-ui": path.resolve(__dirname, "./src/components/ui"),
      // A common setup maps the UI components directory directly:
      '@repo/shadcn-ui/components/ui': path.resolve(__dirname, './src/components/ui'),
      
      // And the utility library:
      '@repo/shadcn-ui/lib/utils': path.resolve(__dirname, './src/lib/utils'),

      // FIXES 'refractor/lang/tsx.js', 'refractor/lang/javascript.js', etc.
      'refractor/lang': `${NODE_MODULES_PATH}/refractor/lang`,
      
      // FIXES 'refractor/lib/core'
      'refractor/lib/core': `${NODE_MODULES_PATH}/refractor/lib/core.js`
    },
  },
  optimizeDeps: {
    // optionally force pre-bundle
    include: [
      "react",
      "react-dom"
    ]
  }

})
