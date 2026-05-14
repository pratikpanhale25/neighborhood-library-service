import { describe, expect, it } from "vitest";
import { renderHook, act } from "@testing-library/react";

import { useAsyncAction } from "./use-async-action";

describe("useAsyncAction", () => {
  it("returns the async result and clears pending in finally", async () => {
    const { result } = renderHook(() => useAsyncAction());
    let v: string | undefined;
    await act(async () => {
      v = await result.current.run(async () => "ok");
    });
    expect(v).toBe("ok");
    expect(result.current.pending).toBe(false);
  });
});
