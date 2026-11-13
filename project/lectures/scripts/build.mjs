#!/usr/bin/env node
// Сборка лекционных слайдов: project/lectures/<id>/slides.md -> public/lectures/<id>.{pdf,pptx}
//
//   node scripts/build.mjs                 все лекции (каталоги с "_" в начале пропускаются)
//   node scripts/build.mjs 01-intro        одна лекция (можно несколько; "_template" — образец)
//   node scripts/build.mjs --list          список лекций
//   node scripts/build.mjs --serve 01-intro  предпросмотр в браузере с автообновлением
//   --pdf / --pptx                         только один формат
//
// Переменные окружения:
//   CHROME_PATH    путь к Chrome/Chromium (иначе ищется автоматически)
//   PPTX_EDITABLE  =1 — редактируемый PPTX (экспериментально, требует LibreOffice)
//   OUT_DIR        каталог результата (по умолчанию <repo>/public/lectures)

import { spawnSync } from 'node:child_process'
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const repo = resolve(root, '..', '..')
const outDir = resolve(process.env.OUT_DIR ?? join(repo, 'public', 'lectures'))
const buildDir = join(root, '.build')
const marpBin = join(root, 'node_modules', '.bin', 'marp')

const args = process.argv.slice(2)
const flags = new Set(args.filter((a) => a.startsWith('--')))
const wanted = args.filter((a) => !a.startsWith('--')).map((a) => a.replace(/\/+$/, ''))

function die(message) {
  console.error(`Ошибка: ${message}`)
  process.exit(1)
}

function lectures({ withHidden = false } = {}) {
  return readdirSync(root, { withFileTypes: true })
    .filter((e) => e.isDirectory() && existsSync(join(root, e.name, 'slides.md')))
    .map((e) => e.name)
    .filter((name) => withHidden || !name.startsWith('_'))
    .sort()
}

// Шрифты встраиваются в тему как data: URI — сборка не зависит от сети и системных шрифтов.
function fontFaces() {
  const subsets = /-(cyrillic|cyrillic-ext|latin|latin-ext)-\d+-(normal|italic)\.woff2/
  const sources = [
    ['inter', ['400', '400-italic', '500', '600', '700']],
    ['jetbrains-mono', ['400', '600']],
  ]
  let css = ''
  for (const [font, weights] of sources) {
    const dir = join(root, 'node_modules', '@fontsource', font)
    if (!existsSync(dir)) die('зависимости не установлены: выполните `make setup`')
    for (const weight of weights) {
      const blocks = readFileSync(join(dir, `${weight}.css`), 'utf8').match(/@font-face\s*{[^}]*}/g) ?? []
      for (const block of blocks) {
        const file = block.match(/url\(\.\/(files\/[^)]+\.woff2)\)/)?.[1]
        if (!file || !subsets.test(file)) continue
        const data = readFileSync(join(dir, file)).toString('base64')
        css += block.replace(/src:[^;]*;/, `src: url(data:font/woff2;base64,${data}) format('woff2');`) + '\n'
      }
    }
  }
  return css
}

function buildTheme() {
  mkdirSync(buildDir, { recursive: true })
  const theme = readFileSync(join(root, 'theme', 'ctf-academic.css'), 'utf8')
  // @import обязан стоять до остальных правил, поэтому @font-face вставляются после него.
  const marker = "@import 'default';"
  if (!theme.includes(marker)) die(`в теме не найдена строка ${marker}`)
  const out = join(buildDir, 'ctf-academic.css')
  writeFileSync(out, theme.replace(marker, `${marker}\n${fontFaces()}`))
  return out
}

function findBrowser() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH
  for (const name of ['chromium', 'chromium-browser', 'google-chrome', 'google-chrome-stable', 'microsoft-edge']) {
    const found = spawnSync('which', [name], { encoding: 'utf8' })
    if (found.status === 0) return found.stdout.trim()
  }
  // Chromium, установленный Playwright (npx playwright install chromium).
  const cache = join(homedir(), '.cache', 'ms-playwright')
  if (existsSync(cache)) {
    const builds = readdirSync(cache).filter((d) => /^chromium-\d+$/.test(d))
    builds.sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]))
    for (const build of builds) {
      for (const sub of ['chrome-linux64', 'chrome-linux']) {
        const bin = join(cache, build, sub, 'chrome')
        if (existsSync(bin)) return bin
      }
    }
  }
  return null // Marp попробует найти браузер сам
}

function marp(marpArgs, env) {
  // Без --no-stdin Marp ждёт ввода, если stdin не терминал (CI, конвейеры).
  const result = spawnSync(marpBin, ['--no-stdin', ...marpArgs], { stdio: ['ignore', 'inherit', 'inherit'], env })
  if (result.status !== 0) die(`marp завершился с кодом ${result.status}`)
}

if (flags.has('--list')) {
  console.log(lectures().join('\n'))
  process.exit(0)
}

if (!existsSync(marpBin)) die('зависимости не установлены: выполните `make setup`')

const all = lectures({ withHidden: true })
const targets = wanted.length ? wanted : lectures()
for (const id of targets) {
  if (!all.includes(id)) die(`лекция «${id}» не найдена. Доступные: ${all.join(', ') || '—'}`)
}
if (!targets.length) {
  console.log('Лекций пока нет: создайте первую командой `make lecture-new LECTURE=01-intro`.')
  process.exit(0)
}

const theme = buildTheme()
const browser = findBrowser()
const env = { ...process.env, ...(browser ? { CHROME_PATH: browser } : {}) }
const common = ['--theme', theme, '--html', '--allow-local-files']

if (flags.has('--serve')) {
  if (targets.length !== 1) die('для предпросмотра укажите одну лекцию')
  marp([...common, '--server', join(root, targets[0])], env)
  process.exit(0)
}

const formats = ['pdf', 'pptx'].filter((f) => flags.has(`--${f}`) || !(flags.has('--pdf') || flags.has('--pptx')))
mkdirSync(outDir, { recursive: true })

for (const id of targets) {
  const input = join(root, id, 'slides.md')
  const name = id.replace(/^_/, '')
  for (const format of formats) {
    const output = join(outDir, `${name}.${format}`)
    // PDF_NOTES=0 — собрать PDF без заметок докладчика (студенческий комплект).
    const pdfNotes = process.env.PDF_NOTES === '0' ? [] : ['--pdf-notes']
    const extra =
      format === 'pdf'
        ? ['--pdf', '--pdf-outlines', ...pdfNotes]
        : ['--pptx', ...(process.env.PPTX_EDITABLE === '1' ? ['--pptx-editable'] : [])]
    marp([...common, ...extra, '-o', output, input], env)
  }
}
console.log(`\nГотово: ${outDir}`)
