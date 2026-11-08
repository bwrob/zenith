#set page(width: auto, height: auto, margin: 4pt, fill: none)

#let light-grad = gradient.linear(
  (rgb("#38bdf8"), 0%),
  (rgb("#0ea5e9"), 25%),
  (rgb("#0284c7"), 55%),
  (rgb("#0369a1"), 78%),
  (rgb("#0f172a"), 92%),
  (rgb("#020408"), 100%),
)

#let spec = (
  font: "Cinzel",
  weight: "bold",
  tracking: 2.5pt,
  top-edge: "bounds",
  bottom-edge: "bounds",
)

#context {
  let target-h = 52.64pt
  let probe = measure(text(..spec, size: 100pt)[ZENITH])
  let sz = 100pt * (target-h / probe.height)
  grid(
    columns: (auto, auto),
    gutter: 16pt,
    align: horizon,
    image("zenith-star.svg", width: 56pt, height: 56pt),
    box[
      #set text(..spec, size: sz)
      #place(
        top + left,
        dx: 0pt,
        dy: 0.6pt,
        text(
          fill: rgb("#0f172a").transparentize(82%),
          stroke: (paint: rgb("#0f172a").transparentize(82%), thickness: 1.0pt, join: "round"),
        )[ZENITH],
      )
      #place(
        top + left,
        text(
          fill: rgb("#080c14"),
          stroke: (paint: rgb("#0369a1").transparentize(55%), thickness: 0.75pt, join: "round"),
        )[ZENITH],
      )
      #text(fill: light-grad)[ZENITH]
    ],
  )
}
