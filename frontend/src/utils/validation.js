export const MAX_AMOUNT = 100_000_000;
export const MAX_TEXT_LENGTH = 255;
export const MAX_MEMO_LENGTH = 1000;

export function isPositiveAmount(value, max = MAX_AMOUNT) {
  return typeof value === "number" && Number.isFinite(value) && value > 0 && value <= max;
}

export function isNonNegativeAmount(value, max = MAX_AMOUNT) {
  return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= max;
}

export function isNonEmptyWithinLength(value, maxLength = MAX_TEXT_LENGTH) {
  const trimmed = (value ?? "").trim();
  return trimmed.length > 0 && trimmed.length <= maxLength;
}

export function isWithinLength(value, maxLength = MAX_MEMO_LENGTH) {
  return (value ?? "").trim().length <= maxLength;
}
