# frontend

React/Next.js frontend following **Atomic Design**.

## Structure
```
components/
  atoms/       # Button, Input, Label — no business logic
  molecules/   # FormField, Card — compositions of atoms
  organisms/   # FormularioEmpresa, TablaProductos — full UI blocks
templates/     # Page layouts (header + content slots)
app/           # Next.js App Router pages
```
