# Recharts 3 type migration findings

Recharts 3 exports `TooltipContentProps` with `payload`, `label`, `active`, and related context fields, while `React.ComponentProps<typeof Tooltip>` intentionally omits context-controlled fields such as `payload` and `label`. The custom tooltip must therefore use `TooltipContentProps` rather than component props.

Recharts 3 exports `LegendProps` from `component/Legend`, but its props intentionally omit `payload`; the custom legend should define its payload using the exported `LegendPayload` type from `component/DefaultLegendContent` or a narrow local shape and use `verticalAlign` separately.
