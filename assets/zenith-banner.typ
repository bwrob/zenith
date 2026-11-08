#set page(width: auto, height: auto, margin: 4pt, fill: none)

#let dark-grad = gradient.linear(
  (rgb("#ffffff"), 0%),
  (rgb("#bae6fd"), 24%),
  (rgb("#7dd3fc"), 55%),
  (rgb("#38bdf8"), 85%),
  (rgb("#0ea5e9"), 100%),
  angle: 18deg,
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
    box(width: 56pt, height: 56pt)[
      #image("zenith-star.svg", width: 56pt, height: 56pt)
      #place(
        center + horizon,
        circle(
          radius: 26.32pt,
          fill: none,
          stroke: 0.75pt + gradient.linear(
            rgb("#7dd3fc").transparentize(40%),
            rgb("#38bdf8").transparentize(65%),
            rgb("#1e293b").transparentize(40%),
            angle: 135deg,
          ),
        ),
      )
    ],
    box[
      #set text(..spec, size: sz)
      #place(
        top + left,
        dx: 0pt,
        dy: 0.85pt,
        text(
          fill: rgb("#020408").transparentize(50%),
          stroke: (paint: rgb("#020408").transparentize(50%), thickness: 3.2pt, join: "round"),
        )[ZENITH],
      )
      #place(
        top + left,
        text(
          fill: rgb("#020408"),
          stroke: (paint: rgb("#020408"), thickness: 2.2pt, join: "round"),
        )[ZENITH],
      )
      #text(fill: dark-grad)[ZENITH]
    ],
  )
}
