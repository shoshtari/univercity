import { BASE_URL } from "../configs/api";

class ApiError extends Error {
  constructor(status, message, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

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

export async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new ApiError(response.status, body.error, body.details);
  }

  return response.json();
}
