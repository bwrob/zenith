#set page(width: auto, height: auto, margin: 4pt, fill: none)

#block(
  stroke: 1.25pt + rgb("#cbd5e1"),
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
        fill: gradient.linear(
          (rgb("#0ea5e9"), 0%),
          (rgb("#0284c7"), 40%),
          (rgb("#0369a1"), 75%),
          (rgb("#090d16"), 100%),
        ),
      )[ZENITH]
    ],
  )
]
