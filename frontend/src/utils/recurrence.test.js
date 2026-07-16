import { describe, expect, it } from "vitest";
import { scheduleOccursOnDate } from "./recurrence.js";

describe("scheduleOccursOnDate", () => {
  it("non-recurring: matches only the exact origin date", () => {
    const schedule = { start_datetime: "2026-07-01T10:00:00", recurrence_type: "none" };
    expect(scheduleOccursOnDate(schedule, "2026-07-01")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-07-02")).toBe(false);
  });

  it("treats a missing recurrence_type the same as none", () => {
    const schedule = { start_datetime: "2026-07-01T10:00:00" };
    expect(scheduleOccursOnDate(schedule, "2026-07-01")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-08-01")).toBe(false);
  });

  it("never occurs before the origin date, even for recurring schedules", () => {
    const schedule = { start_datetime: "2026-07-10T10:00:00", recurrence_type: "weekly" };
    expect(scheduleOccursOnDate(schedule, "2026-07-03")).toBe(false);
  });

  it("stops occurring after recurrence_end (exclusive) but still occurs on recurrence_end itself", () => {
    const schedule = {
      start_datetime: "2026-07-01T10:00:00",
      recurrence_type: "weekly",
      recurrence_end: "2026-07-15",
    };
    expect(scheduleOccursOnDate(schedule, "2026-07-15")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-07-22")).toBe(false);
  });

  it("weekly: occurs on every date with the same day of week as the origin", () => {
    const schedule = { start_datetime: "2026-07-01T10:00:00", recurrence_type: "weekly" };
    expect(scheduleOccursOnDate(schedule, "2026-07-08")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-07-09")).toBe(false);
  });

  it("monthly: occurs on every date with the same day of month as the origin", () => {
    const schedule = { start_datetime: "2026-07-15T10:00:00", recurrence_type: "monthly" };
    expect(scheduleOccursOnDate(schedule, "2026-08-15")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-08-16")).toBe(false);
  });

  it("monthly: never matches a shorter month that lacks the origin day", () => {
    const schedule = { start_datetime: "2026-01-31T10:00:00", recurrence_type: "monthly" };
    expect(scheduleOccursOnDate(schedule, "2026-03-31")).toBe(true);
    expect(scheduleOccursOnDate(schedule, "2026-04-30")).toBe(false);
  });

  it("returns false for an unrecognized recurrence_type", () => {
    const schedule = { start_datetime: "2026-07-01T10:00:00", recurrence_type: "yearly" };
    expect(scheduleOccursOnDate(schedule, "2026-07-01")).toBe(false);
  });
});
