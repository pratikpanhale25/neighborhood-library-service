import type { ReactNode } from "react";

export type DataTableColumn<Row> = {
  header: string;
  headerClassName?: string;
  cellClassName?: string;
  cell: (row: Row) => ReactNode;
};

type DataTableProps<Row> = {
  columns: Array<DataTableColumn<Row>>;
  rows: Row[];
  rowKey: (row: Row) => string;
  emptyMessage: string;
  isLoading?: boolean;
};

/**
 * Shared list table chrome so list pages stay visually consistent and easier to maintain.
 */
export function DataTable<Row>({ columns, rows, rowKey, emptyMessage, isLoading }: DataTableProps<Row>) {
  return (
    <div className="overflow-x-auto rounded border border-zinc-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-zinc-200 bg-zinc-50 text-zinc-700">
          <tr>
            {columns.map((c, i) => (
              <th key={i} className={`px-3 py-2 font-medium ${c.headerClassName ?? ""}`}>
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td className="px-3 py-4 text-zinc-500" colSpan={columns.length}>
                Loading…
              </td>
            </tr>
          ) : rows.length === 0 ? (
            <tr>
              <td className="px-3 py-4 text-zinc-500" colSpan={columns.length}>
                {emptyMessage}
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr key={rowKey(row)} className="border-b border-zinc-100">
                {columns.map((c, i) => (
                  <td key={i} className={`px-3 py-2 ${c.cellClassName ?? ""}`}>
                    {c.cell(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
