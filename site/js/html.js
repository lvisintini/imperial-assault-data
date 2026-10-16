// Tagged template that escapes interpolated values. Nested html`` results, and arrays of them, pass through as-is.
class Html {
  constructor(text) {
    this.text = text;
  }

  toString() {
    return this.text;
  }
}

const ESCAPES = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'};

function format(value) {
  if (value instanceof Html) return value.text;
  if (Array.isArray(value)) return value.map(format).join('');
  if (value == null || value === false) return '';
  return String(value).replace(/[&<>"']/g, c => ESCAPES[c]);
}

export function html(strings, ...values) {
  return new Html(strings.reduce((out, s, i) => out + s + (i < values.length ? format(values[i]) : ''), ''));
}
