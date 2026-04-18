import {ScheduleCellMarginX} from "../../configs/sizes";

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

export const START_HOUR = 7;
export const END_HOUR = 18;
export const TOTAL_HOURS = END_HOUR - START_HOUR;

export function timeToHour(timeStr) {
  const [h, m] = timeStr.split(":").map(Number);
  return h + m / 60;
}

 function hourToPercent(hour) {
  return ((hour - START_HOUR) / TOTAL_HOURS) * 100;
}
export function getLeftAndWidth(start, end) {
  const left = 100 - hourToPercent(end) + ScheduleCellMarginX;
  const width = 100 - hourToPercent(start) - left - ScheduleCellMarginX;
  return { left, width };
}
export function getOpacity(state) {
	switch(state) {
		case "selected": return 0.85;
		case "pending": return 0.5;
		default: return 1;
	}
}


