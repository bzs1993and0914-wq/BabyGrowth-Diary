/** 将记录日期 `YYYY-MM-DD` 解析为本地日历日，避免 `Date` 字符串解析的时区偏差。 */
export function parseLocalYmd(dateStr: string): Date {
  const [y, m, d] = dateStr.split('-').map(Number)
  return new Date(y, m - 1, d)
}

/**
 * ISO 8601 周序：周一为一周之首，包含当年第一个周四的那一周为第 1 周。
 * 返回的 isoYear 可能与日历年份不同（年初/年末边界）。
 */
export function getISOWeekData(date: Date): { isoYear: number; isoWeek: number } {
  const dayCalendar = new Date(date.getFullYear(), date.getMonth(), date.getDate())
  const dayNr = (dayCalendar.getDay() + 6) % 7
  const thursday = new Date(dayCalendar)
  thursday.setDate(dayCalendar.getDate() + 3 - dayNr)
  const isoYear = thursday.getFullYear()
  const jan4 = new Date(isoYear, 0, 4)
  const jan4Day = (jan4.getDay() + 6) % 7
  const week1Monday = new Date(isoYear, 0, 4 - jan4Day)
  const thisMonday = new Date(
    dayCalendar.getFullYear(),
    dayCalendar.getMonth(),
    dayCalendar.getDate() - dayNr,
  )
  const diffDays = Math.round(
    (thisMonday.getTime() - week1Monday.getTime()) / 86_400_000,
  )
  const isoWeek = 1 + Math.floor(diffDays / 7)
  return { isoYear, isoWeek }
}

export function formatIsoWeekTitle(isoYear: number, isoWeek: number): string {
  return `${isoYear}-W${String(isoWeek).padStart(2, '0')}`
}
