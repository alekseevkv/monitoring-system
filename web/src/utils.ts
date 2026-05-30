export type TimeDifference = {
  years: number;
  months: number;
  days: number;
  hours: number;
  minutes: number;
  seconds: number;
  totalDays: number;
  isFuture: boolean;
};

export function getTimeDifference(target: Date | string): TimeDifference {
  const targetDate = new Date(target);
  if (isNaN(targetDate.getTime())) {
    throw new TypeError(`Invalid date: ${target}`);
  }

  const now = new Date();
  const isFuture = targetDate > now;
  const [start, end] = isFuture ? [now, targetDate] : [targetDate, now];

  let years = end.getFullYear() - start.getFullYear();
  let months = end.getMonth() - start.getMonth();
  let days = end.getDate() - start.getDate();

  if (days < 0) {
    months--;
    const daysInPrevMonth = new Date(
      end.getFullYear(),
      end.getMonth(),
      0,
    ).getDate();
    days += daysInPrevMonth;
  }
  if (months < 0) {
    years--;
    months += 12;
  }

  const startAligned = new Date(start);
  startAligned.setFullYear(end.getFullYear(), end.getMonth(), end.getDate());
  const msDiff = end.getTime() - startAligned.getTime();

  const hours = Math.floor(msDiff / 3_600_000);
  const minutes = Math.floor((msDiff % 3_600_000) / 60_000);
  const seconds = Math.floor((msDiff % 60_000) / 1_000);

  const totalDays = Math.floor(
    Math.abs(end.getTime() - start.getTime()) / 86_400_000,
  );

  return { years, months, days, hours, minutes, seconds, totalDays, isFuture };
}

export type MonthStyle = 'long' | 'short' | 'narrow';

export function getMonthName(
  date: Date | string | number | null | undefined,
  locale: string = 'ru-RU',
  style: MonthStyle = 'long',
): string {
  if (!date) return '';

  const d = new Date(date);
  if (isNaN(d.getTime())) return '';

  return new Intl.DateTimeFormat(locale, { month: style }).format(d);
}
