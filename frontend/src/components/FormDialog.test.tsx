import type { FormEvent } from "react";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import { FormDialog } from "./FormDialog";

describe("FormDialog", () => {
  it("renders nothing when closed", () => {
    const { container } = render(
      <FormDialog
        open={false}
        title="T"
        submitLabel="Go"
        pending={false}
        onClose={() => {}}
        onSubmit={(e) => e.preventDefault()}
      >
        <p>child</p>
      </FormDialog>,
    );
    expect(container.firstChild).toBeNull();
  });

  it("disables submit while pending to block duplicate submits", () => {
    const onSubmit = vi.fn((e: FormEvent<HTMLFormElement>) => e.preventDefault());
    render(
      <FormDialog open title="Add" submitLabel="Create" pending onClose={() => {}} onSubmit={onSubmit}>
        <input name="x" />
      </FormDialog>,
    );
    const submit = screen.getByRole("button", { name: "Create" });
    expect(submit).toBeDisabled();
    fireEvent.click(submit);
    expect(onSubmit).not.toHaveBeenCalled();
  });
});
