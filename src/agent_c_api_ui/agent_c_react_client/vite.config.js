import path from "path"
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
    extensions: ['.js', '.jsx', '.ts', '.tsx']
  },
    define: {
    __API_URL__: JSON.stringify(process.env.VITE_API_URL),
  },
  server: {
    host: true,
    https: {
      key: fs.readFileSync('../../../agent_c_config/localhost_self_signed-key.pem'),
      cert: fs.readFileSync('../../../agent_c_config/localhost_self_signed.pem'),
    },
    strictPort: true,
    allowedHosts: process.env.VITE_ALLOWED_HOSTS
      ? process.env.VITE_ALLOWED_HOSTS.split(',').map(host => host.trim())
      : ['localhost', '.local']
  },

})
