// Tiny i18n helper. Strings come from the server (window.I18N), already in the page language.
function tr(key, vars) {
  let s = window.I18N[key];
  if (s === undefined) return key;
  if (vars) for (const [k, v] of Object.entries(vars)) s = s.replaceAll(`{${k}}`, v);
  return s;
}
