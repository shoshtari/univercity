import { BASE_URL } from "../configs/api";

class ApiResult {
  constructor({ok, data = null, error = null}) {
    this.ok = ok;
    this.data = data;
    this.error = error;
    if (this.ok && this.error !== null) {
      throw new Error("ok result cannot have error");
    }
    if (!this.ok && this.error === null) {
      throw new Error("error result must have error");
    }
  }
}
export function ApiResultOk(data) {
  return new ApiResult({ ok: true, data, error: null });
}

export function ApiResultErr(error) {
  return new ApiResult({ ok: false, data: null, error });
}
