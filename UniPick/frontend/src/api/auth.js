import { MOCK_APIS } from "../configs/api";
import { request } from "./client";
import { mockDelay } from "./mock";
import { ApiResultOk, ApiResultErr } from "./result";

export async function login(username, password) {
  if (MOCK_APIS) {
    await mockDelay();
    return new ApiResultOk({ access_token: "dummyaccesstoken" });
  }
  try {
    const result = await request({
      path: "/auth/login",
      options: {
        body: JSON.stringify({
          username: username,
          password: password,
        }),
        method: "POST",
      },
    });

    return new ApiResultOk(result);
  } catch (err) {
    return new ApiResultErr(err);
  }
}

export async function signup(username, password) {
  if (MOCK_APIS) {
    await mockDelay();
    return new ApiResultOk(null);
  }
  try {
    const result = await request({
      path: "/auth/signup",
      options: {
        body: JSON.stringify({
          username: username,
          password: password,
        }),
        method: "POST",
      },
    });

    return new ApiResultOk(result);
  } catch (err) {
    if (err.status === 400 && err.message === "validation_error") {
      const detail = err.details?.[0];
      return new ApiResultErr(
        detail ? `${detail.loc} is not valid` : "validation error",
      );
    }
    return new ApiResultErr(err);
  }
}

export async function getMe(accessToken) {
  if (MOCK_APIS) {
    await mockDelay();
    return new ApiResultOk({ username: "mockuser" });
  }

  try {
    const result = await request({
      path: "/auth/getme",
      options: {
        method: "GET",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      },
    });

    return new ApiResultOk(result);
  } catch (err) {
    return new ApiResultErr(err);
  }
}
