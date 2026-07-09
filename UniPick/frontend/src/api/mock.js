import { MOCK_DELAY_MS } from "../configs/api";

export function mockDelay() {
  return new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));
}
