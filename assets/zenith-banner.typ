#set page(width: auto, height: auto, margin: 8pt, fill: none)

#block(
  fill: rgb("#060a12"),
  stroke: (
    paint: gradient.linear(
      rgb("#38bdf8").transparentize(20%),
      rgb("#0284c7").transparentize(70%),
      rgb("#1e293b"),
      angle: 135deg,
    ),
    thickness: 1.25pt,
  ),
  radius: 16pt,
  inset: (x: 24pt, y: 16pt),
)[
  #grid(
    columns: (auto, auto, auto),
    gutter: 22pt,
    align: horizon,
    image("zenith-star.svg", height: 72pt),
    line(start: (0pt, -30pt), end: (0pt, 30pt), stroke: 1pt + rgb("#1e293b")),
    [
      #set text(font: ("Inter", "SF Pro Display", "Liberation Sans", "Noto Sans", "sans-serif"))
      #stack(
        spacing: 6pt,
        text(
          size: 42pt,
          weight: "bold",
          tracking: 4pt,
          fill: gradient.linear(rgb("#ffffff"), rgb("#e0f2fe"), rgb("#38bdf8")),
        )[ZENITH],
        grid(
          columns: (auto, auto),
          gutter: 10pt,
          align: horizon,
          box(
            fill: rgb("#0c1527"),
            stroke: 0.75pt + rgb("#38bdf8").transparentize(40%),
            radius: 4pt,
            inset: (x: 7pt, y: 3pt),
            text(size: 8.5pt, weight: "bold", tracking: 1.5pt, fill: rgb("#38bdf8"))[SCAFFOLDING],
          ),
          text(size: 10.5pt, weight: "medium", tracking: 1.5pt, fill: rgb("#94a3b8"))[MODERN PYTHON 3.12+],
        ),
      )
    ],
  )
]
