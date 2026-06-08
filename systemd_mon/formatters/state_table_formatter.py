from systemd_mon.formatters.base import Base


class StateTableFormatter(Base):
    """Renders a unit's changed state values as a plain-text table, one column
    per changed field and one row per state snapshot in time."""

    def as_text(self):
        table = self._render_table()
        columns = list(zip(*table))
        lengths = [max(len(cell) for cell in col) for col in columns]

        full_width = sum(lengths) + (len(lengths) * 3) + 1
        div = " " + ("-" * full_width) + "\n"
        out = div
        for row in table:
            out += " | "
            for i, col in enumerate(row):
                out += col.ljust(lengths[i]) + " | "
            out += "\n" + div
        return out

    def _render_table(self):
        changed = self.unit.state_change.diff()
        table = []
        table.append(["Time"] + [row[0].display_name for row in changed])
        for vals in zip(*changed):
            table.append([self._format_time(vals[0].timestamp)] +
                         [v.value for v in vals])
        return table

    @staticmethod
    def _format_time(dt):
        # Equivalent to Ruby's "%H:%M:%S.%3N %z" (millisecond precision). Naive
        # datetimes produce an empty %z, matching local-time behaviour.
        return (dt.strftime("%H:%M:%S.") +
                "%03d" % (dt.microsecond // 1000) +
                dt.strftime(" %z"))
