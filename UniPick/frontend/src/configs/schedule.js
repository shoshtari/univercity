export const SCHEDULE_START_HOUR = 7;
export const SCHEDULE_END_HOUR = 18;
export const SCHEDULE_TOTAL_HOURS = SCHEDULE_END_HOUR - SCHEDULE_START_HOUR;

export const DAYS = ["Sat", "Sun", "Mon", "Tue", "Wed"];

export const DAY_MAP = {
  Sat: "Saturday",
  Sun: "Sunday",
  Mon: "Monday",
  Tue: "Tuesday",
  Wed: "Wednesday",
};

export const DAY_PERSIAN_MAP = {
  Sat: "شنبه",
  Sun: "یکشنبه",
  Mon: "دوشنبه",
  Tue: "سه‌شنبه",
  Wed: "چهارشنبه",
};

export const SCHEDULE_CELL_STATE = {
  SELECTED: "selected",
  PENDING: "pending",
  DEFAULT: "default",
};

export const SCHEDULE_CELL_OPACITY = {
  [SCHEDULE_CELL_STATE.SELECTED]: 0.85,
  [SCHEDULE_CELL_STATE.PENDING]: 0.5,
  [SCHEDULE_CELL_STATE.DEFAULT]: 1,
};
