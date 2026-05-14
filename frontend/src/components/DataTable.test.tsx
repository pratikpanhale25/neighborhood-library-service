import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";

import { DataTable } from "./DataTable";

describe("DataTable", () => {
  it("renders headers and row cells", () => {
    render(
      <DataTable
        rowKey={(r) => r.id}
        emptyMessage="empty"
        rows={[{ id: "1", name: "A" }]}
        columns={[
          { header: "ID", cell: (r) => r.id },
          { header: "Name", cell: (r) => r.name },
        ]}
      />,
    );
    expect(screen.getByText("ID")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
    expect(screen.getByText("A")).toBeInTheDocument();
  });

  it("shows emptyMessage when there are no rows and not loading", () => {
    render(
      <DataTable
        rowKey={(r: { id: string }) => r.id}
        emptyMessage="No rows"
        rows={[]}
        columns={[{ header: "H", cell: () => null }]}
      />,
    );
    expect(screen.getByText("No rows")).toBeInTheDocument();
  });
});
