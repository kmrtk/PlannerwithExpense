function parseDateKey(key) {
  const [y, m, d] = key.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export function scheduleOccursOnDate(schedule, dateKey) {
  const originKey = schedule.start_datetime.slice(0, 10);
  if (!schedule.recurrence_type || schedule.recurrence_type === "none") {
    return originKey === dateKey;
  }
  if (dateKey < originKey) return false;
  if (schedule.recurrence_end && dateKey > schedule.recurrence_end) return false;

  const origin = parseDateKey(originKey);
  const target = parseDateKey(dateKey);

  if (schedule.recurrence_type === "weekly") {
    return origin.getDay() === target.getDay();
  }
  if (schedule.recurrence_type === "monthly") {
    return origin.getDate() === target.getDate();
  }
  return false;
}
