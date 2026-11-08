#set page(width: auto, height: auto, margin: 4pt, fill: none)

#block(
  stroke: 1.25pt + rgb("#000000"),
  radius: 10pt,
  inset: (x: 14pt, y: 8pt),
)[
  #grid(
    columns: (auto, auto),
    gutter: 16pt,
    align: horizon,
    image("zenith-star.svg", height: 48pt),
    [
      #set text(font: "Space Grotesk", size: 68.6pt, weight: "bold", tracking: 2pt)
      #text(
        fill: gradient.linear(rgb("#ffffff"), rgb("#e0f2fe"), rgb("#38bdf8")),
        stroke: 0.5pt + rgb("#000000"),
      )[ZENITH]
    ],
  )
]
