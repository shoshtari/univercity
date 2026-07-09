import { ScheduleCellMarginX } from "../../configs/sizes";
import {
  SCHEDULE_START_HOUR,
  SCHEDULE_TOTAL_HOURS,
  SCHEDULE_CELL_OPACITY,
  DAYS,
  DAY_MAP,
  DAY_PERSIAN_MAP,
} from "../../configs/schedule";

export { DAYS, DAY_MAP, DAY_PERSIAN_MAP };

export function timeToHour(timeStr) {
  const [h, m] = timeStr.split(":").map(Number);
  return h + m / 60;
}

function hourToPercent(hour) {
  return ((hour - SCHEDULE_START_HOUR) / SCHEDULE_TOTAL_HOURS) * 100;
}

export function getLeftAndWidth(start, end) {
  const left = 100 - hourToPercent(end) + ScheduleCellMarginX;
  const width = 100 - hourToPercent(start) - left - ScheduleCellMarginX;
  return { left, width };
}

export function getOpacity(state) {
  return SCHEDULE_CELL_OPACITY[state] ?? SCHEDULE_CELL_OPACITY.default;
}
