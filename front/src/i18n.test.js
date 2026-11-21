import { describe, expect, it } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import {
  dictionaries,
  t,
  setLanguage,
  getLanguage,
  plural,
  formatDate,
  formatDuration,
  apiError,
  translateMessage,
} from './i18n'

describe('complete local dictionaries', () => {
  it('has matching nonempty translations and interpolation parameters', () => {
    expect(Object.keys(dictionaries.ru).sort()).toEqual(Object.keys(dictionaries.en).sort())
    for (const key of Object.keys(dictionaries.en)) {
      expect(dictionaries.ru[key].trim(), key).not.toBe('')
      expect(dictionaries.ru[key].match(/\{\w+\}/g) || [], key).toEqual(
        dictionaries.en[key].match(/\{\w+\}/g) || [],
      )
      expect(dictionaries.ru[key], key).not.toContain('\uFFFD')
    }
    const files = fs
      .readdirSync(path.resolve('src'))
      .filter((name) => /\.(jsx|js)$/.test(name) && !name.includes('.test.'))
    for (const file of files) {
      const source = fs.readFileSync(path.resolve('src', file), 'utf8')
      for (const match of source.matchAll(/\b(?:t|translate)\(['"]([^'"]+)['"]\s*[,)]/g)) {
        expect(dictionaries.ru[match[1]], `${file}: ${match[1]}`).toBeDefined()
      }
    }
    for (const family of [
      ['status', 'active', 'paused', 'completed'],
      ['audio', 'active', 'waiting', 'unavailable', 'muted'],
      ['audio.repeat', 'all', 'off', 'one'],
    ]) {
      const [prefix, ...values] = family
      for (const value of values)
        expect(
          dictionaries.ru[`${prefix}${prefix.endsWith('repeat') ? '_' : '.'}${value}`],
        ).toBeDefined()
    }
  })
  it('switches immediately, saves language, and formats Cyrillic plurals and dates', () => {
    setLanguage('ru')
    expect(getLanguage()).toBe('ru')
    expect(document.documentElement.lang).toBe('ru')
    expect(localStorage.getItem('lasttrain:language')).toBe('ru')
    expect(t('ui.settings')).toBe('Настройки')
    expect(formatDate('2026-01-10T12:00:00Z')).toMatch(/янв/)
    expect(formatDuration(119.8)).not.toMatch(/60/)
    setLanguage('en')
    expect(t('ui.settings')).toBe('Settings')
    expect(formatDate('2026-01-10T12:00:00Z')).toMatch(/Jan/)
    setLanguage('invalid')
    expect(getLanguage()).toBe('en')
  })
  it('localizes API validation without altering arbitrary user content', () => {
    setLanguage('ru')
    expect(
      apiError({ duration_minutes: ['Ensure this value is greater than or equal to 1.'] }),
    ).toContain('не меньше 1')
    expect(translateMessage('Failed to fetch')).toContain('Last Train')
    expect(translateMessage('Мой поезд — Dawn 🚂')).toBe('Мой поезд — Dawn 🚂')
    expect([1, 2, 5, 21].map((count) => plural('count.journeys', count))).toEqual([
      '1 поездка',
      '2 поездки',
      '5 поездок',
      '21 поездка',
    ])
  })
})
