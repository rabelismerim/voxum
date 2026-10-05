/* eslint-disable n/prefer-global/process */
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitest/config'
import { loadEnv } from 'vite'
import Vue from '@vitejs/plugin-vue'

import UnoCSS from 'unocss/vite'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import Pages from 'vite-plugin-pages'
import Layouts from 'vite-plugin-vue-layouts'
import mkcert from 'vite-plugin-mkcert'
import { quasar } from '@quasar/vite-plugin'
import { QuasarResolver } from 'unplugin-vue-components/resolvers'
import VueMacros from 'unplugin-vue-macros/dist/vite'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// https://vitejs.dev/config/
export default ({ mode }) => {
  process.env = {
    ...process.env,
    ...loadEnv(mode, process.cwd()),
  }
  const minifyOnBuild = (process.env?.VITE_BUILD_MINIFY ?? 'true') === 'true'
  return defineConfig({
    base: process.env.NODE_ENV === 'development' ? '/' : (process.env.VITE_BUILD_BASE_URL ?? '/'),
    define: {
      APP_VERSION: JSON.stringify(process.env.npm_package_version),
    },
    build: {
      outDir: path.resolve(__dirname, process.env.VITE_BUILD_PATH ?? './dist'),
      minify: minifyOnBuild,
    },
    resolve: {
      alias: {
        '@/': `${path.resolve(__dirname, 'src')}/`,
      },
    },
    server: {
      https: process.env.VITE_HTTPS !== 'false',
      proxy: mode === 'devlocal'
        ? {
            '/voxum/api': {
              target: 'http://127.0.0.1:8000',
              changeOrigin: true,
            },
            '/voxum/ws': {
              target: 'http://127.0.0.1:8000',
              changeOrigin: true,
              ws: true,
            },
          }
        : undefined,
    },
    plugins: [
      UnoCSS(),
      Layouts(),
      mkcert(),
      Pages({
        extensions: ['vue'],
      }),
      VueMacros({
        plugins: {
          vue: Vue(),
        },
      }),
      quasar({
        autoImportComponentCase: 'pascal',
      }),
      Components({
        extensions: ['vue', 'md'],
        include: [/\.vue$/, /\.vue\?vue/, /\.md$/],
        resolvers: [QuasarResolver()],
        dts: false,
      }),
      AutoImport({
        imports: [
          'vue',
          'vue-router',
          'vue/macros',
          '@vueuse/core',
          {
            '@/composables/useambient': [
              'useAmbient',
            ],
          },
          {
            '@/composables/useNotification': [
              'throwError',
            ],
          },
          {
            quasar: [
              'useQuasar',
              'copyToClipboard',
            ],
          },
          {
            '@floating-ui/dom': [
              'computePosition',
              'shift',
              'flip',
              'offset',
            ],
          },
          {
            'axios': [
              ['default', 'axios'],
            ],
            'dayjs': [
              ['default', 'dayjs'],
            ],
            '@jrnwn/utils': [
              'typeOf',
              'createEl',
              'setClass',
              'removeClass',
              'setStyle',
              'getSelector',
              'platform',
              'get',
              'set',
              'getListOfPaths',
              'getCookie',
              'setCookie',
              'deleteCookie',
              'normalizeText',
              'toSplit',
              'toCamel',
              'toPascal',
              'toSnake',
              'toKebab',
              'toProperName',
              'range',
            ],
          },
        ],
        dirs: [
          'src/',
          'src/composables',
          'src/stores',
          'src/services',
          'src/directives',
        ],
        vueTemplate: true,
        eslintrc: {
          enabled: true,
        },
      }),
    ],
  })
}
