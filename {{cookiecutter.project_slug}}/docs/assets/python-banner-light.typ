#set page(width: auto, height: auto, margin: 4pt, fill: none)

#block(
  stroke: 1.25pt + rgb("#cbd5e1"),
  radius: 10pt,
  inset: (x: 14pt, y: 8pt),
)[
  #grid(
    columns: (auto, auto),
    gutter: 14pt,
    align: horizon,
    image("python-emblem.svg", height: 48pt),
    [
      #set text(font: "Space Grotesk", size: 68.6pt, weight: "bold", tracking: 2pt)
      #text[
        #text(fill: gradient.linear((rgb("#0ea5e9"), 0%), (rgb("#0284c7"), 50%), (rgb("#1d4e79"), 100%)))[py]#text(fill: gradient.linear((rgb("#f59e0b"), 0%), (rgb("#d97706"), 60%), (rgb("#78350f"), 100%)))[thon]
      ]
    ],
  )
]
