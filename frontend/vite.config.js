
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { rollup } from '@rollup/wasm-node'

export default defineConfig({
  plugins: [react()],
})
